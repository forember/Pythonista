#!/usr/bin/env python3

import os.path
import math

from simplexchunks_py3 import gen_chunk
from random import random
maxdistance = 2**30

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib, GObject
import cairo
from PIL import Image, ImageDraw, ImageFont

MAP_SIZE = 128
CANVAS_SIZE = MAP_SIZE * 2
SCRIPT_DIRPATH = os.path.dirname(__file__)
UBUNTU_FONT_FILENAME = "Ubuntu-R.ttf"
UBUNTU_FONT_FILEPATH = os.path.join(SCRIPT_DIRPATH, UBUNTU_FONT_FILENAME)
CHUNKS_DIRPATH = os.path.join(SCRIPT_DIRPATH, "chunks")
EMPTY_CHUNK = Image.new("RGB", (MAP_SIZE, MAP_SIZE))
MAX_MEM_CHUNKS = 1024
CHUNK_I = 0.0625

def pil_to_pixbuf(im):
    """Convert a PIL image to a Gdk Pixbuf, without alpha."""
    pixels = GLib.Bytes(im.convert("RGB").tobytes("raw", "RGB", 0, 1))
    return GdkPixbuf.Pixbuf.new_from_bytes(
        pixels, GdkPixbuf.Colorspace.RGB, False, 8, im.width, im.height, im.width * 3
    )

class MapWidget(Gtk.EventBox):
    "An interactive map."

    def __init__(self, win):
        Gtk.EventBox.__init__(self)
        self.win = win

        self.chunks = {}

        self.win_width = 1280
        self.win_height = 720

        #self.map_cx = random() * maxdistance
        #self.map_cy = random() * maxdistance
        self.map_cx = self.map_cy = 0

        self.button1_down = False
        self.going_to_update = False
        self.not_top_level_callback = False
        self.crop_rect = 0, 0, 0, 0

        self.image_widget = Gtk.Image()
        self.add(self.image_widget)

        self.im = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE))
        self.update_image()
        self.connect("size-allocate", self.update_display)
        self.connect("button-press-event", self.update_buttons)
        self.connect("button-release-event", self.update_buttons)
        self.connect("motion-notify-event", self.handle_motion)

        GLib.timeout_add(100, lambda: self.update_display() or True)

    def do_get_preferred_width(self):
        #return self.win.get_size().width - 2
        return self.win_width - 2

    def do_get_preferred_width_for_height(self, height):
        return self.do_get_preferred_width()

    def do_get_preferred_height(self):
        #return self.win.get_size().height - 2
        return self.win_height - 2

    def update_buttons(self, widget=None, event=None):
        """Handle a mouse button event."""
        prev_button1_down = self.button1_down
        self.button1_down = bool(event.state & Gdk.ModifierType.BUTTON1_MASK)
        if self.button1_down and not prev_button1_down:
            self.motion_prev_x = event.x
            self.motion_prev_y = event.y

    def handle_motion(self, widget, event):
        """Move the map due to mouse dragging."""
        self.update_buttons(event=event)
        self.map_cx -= event.x - self.motion_prev_x
        self.map_cy -= event.y - self.motion_prev_y
        self.request_full_update()
        self.motion_prev_x = event.x
        self.motion_prev_y = event.y

    def request_full_update(self):
        """Fully redraw the map and overlays in 10 s."""
        if not self.going_to_update:
            self.going_to_update = True
            self.update_display()
            GLib.timeout_add(10000, self.do_full_update_now)

    def do_full_update_now(self, user_data=None):
        """Fully redraw the map and overlays."""
        self.update_image()
        self.update_display()
        self.queue_draw()
        self.going_to_update = False
        return False

    loading_text = "Loading"
    loading_font = ImageFont.truetype(UBUNTU_FONT_FILEPATH, 24)
    loading_wh = loading_font.getsize(loading_text)

    def update_display(self, widget=None, allocation=None, data=None):
        """Resize the virtual canvas, crop, and update the widget."""
        if allocation is None:
            allocation = self.get_allocation()
        self.win_width, self.win_height = self.win.get_size()
        width = min(self.win_width - 2, allocation.width)
        height = min(self.win_height - 2, allocation.height)
        size = max(width, height)
        resized = self.im.resize((size,) * 2)
        x = int(math.ceil((size - width) / 2))
        y = int(math.ceil((size - height) / 2))
        if 2 * x >= resized.width or 2 * y > resized.height:
            return
        self.crop_rect = x, y, resized.width - x, resized.height - y
        cropped = resized.crop(self.crop_rect)
        if self.going_to_update:
            draw = ImageDraw.Draw(cropped)
            cw, ch = cropped.size
            loading_xy = cw - self.loading_wh[0], ch - self.loading_wh[1]
            draw.rectangle((loading_xy, (cw, ch)), fill=(0, 0, 0))
            draw.text(
                loading_xy,
                self.loading_text,
                fill=(255, 255, 255),
                font=self.loading_font,
            )
        pixbuf = pil_to_pixbuf(cropped)
        self.image_widget.set_from_pixbuf(pixbuf)

    def update_image(self):
        """Refetch (usually from memory) and redraw the underlying map."""
        chunk_x = MAP_SIZE * int(self.map_cx / MAP_SIZE) + MAP_SIZE / 2
        chunk_y = MAP_SIZE * int(self.map_cy / MAP_SIZE) + MAP_SIZE / 2
        offset_x = MAP_SIZE * (1 - ((self.map_cx / MAP_SIZE) % 1))
        offset_y = MAP_SIZE * (1 - ((self.map_cy / MAP_SIZE) % 1))
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                cx = chunk_x + dx * MAP_SIZE
                cy = chunk_y + dy * MAP_SIZE
                px = int(offset_x + dx * MAP_SIZE)
                py = int(offset_y + dy * MAP_SIZE)
                chunk = self.fetch_map_chunk(cx, cy)
                #print("{}.paste({}, {})".format(self.im, chunk, (px, py)))
                self.im.paste(chunk, (px, py))

    def fetch_map_chunk(self, cx, cy):
        x = int(cx / MAP_SIZE)
        y = int(cy / MAP_SIZE)
        if (x, y) in self.chunks:
            return self.chunks[x, y]
        basename = "{x:d}.{y:d}.png".format(x=x, y=y)
        filename = os.path.join(CHUNKS_DIRPATH, basename)
        if os.path.exists(filename):
            chunk = Image.open(filename)
        else:
            area = (CHUNK_I * x, -CHUNK_I * y, CHUNK_I, CHUNK_I)
            isize = (MAP_SIZE, MAP_SIZE)
            print("Generating {}".format(basename))
            chunk = gen_chunk(area=area, isize=isize)
            chunk.save(filename)
        if len(self.chunks) >= MAX_MEM_CHUNKS:
            self.chunks = {}
        self.chunks[x, y] = chunk
        return chunk


class MapWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.map = MapWidget(self)
        self.add(self.map)
        self.set_default_size(1280, 720)

def main():
    if not os.path.exists(CHUNKS_DIRPATH):
        os.mkdir(CHUNKS_DIRPATH)
    win = MapWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    raise SystemExit(0)

if __name__ == "__main__":
    main()
