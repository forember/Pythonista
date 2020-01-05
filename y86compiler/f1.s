	.file	"fib.c"
	.text
	.globl	fib
	.type	fib, @function
fib:
.LFB23:
	subl	$28, %esp
	movl	%ebx, 20(%esp)
	movl	%esi, 24(%esp)
	movl	32(%esp), %ebx
	movl	$1, %eax
	cmpl	$1, %ebx
	jle	.L2
	leal	-1(%ebx), %eax
	movl	%eax, (%esp)
	call	fib
	movl	%eax, %esi
	subl	$2, %ebx
	movl	%ebx, (%esp)
	call	fib
	addl	%esi, %eax
.L2:
	movl	20(%esp), %ebx
	movl	24(%esp), %esi
	addl	$28, %esp
	ret
	.string	"fib(%d)=%d\n"
