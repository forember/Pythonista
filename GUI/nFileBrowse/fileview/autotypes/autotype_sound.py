from ..autoview import args


AUTOTYPE_PRIORITY = 0x6fffffff


def AUTOTYPE_FUNC(browser, file_path, title=None, **kwargs):
  import sound
  sound_player = sound.Player(file_path)
  if sound_player.duration:
    from ..SoundPlayer import SoundPlayerPane
    return SoundPlayerPane, args(sound_player, title=title, name=file_path), 1
