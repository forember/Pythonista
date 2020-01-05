	.file	"ncopy.c"
	.text
	.p2align 4,,15
	.globl	ncopy
	.type	ncopy, @function
ncopy:
	pushl	%edi
	xorl	%eax, %eax
	pushl	%esi
	pushl	%ebx
	movl	24(%esp), %edi
	movl	16(%esp), %ebx
	movl	20(%esp), %ecx
	testl	%edi, %edi
	jle	.L2
	.p2align 4,,7
	.p2align 3
.L4:
	movl	(%ebx), %esi
	xorl	%edx, %edx
	addl	$4, %ebx
	movl	%esi, (%ecx)
	addl	$4, %ecx
	testl	%esi, %esi
	setg	%dl
	movl	%edx, %esi
	addl	%esi, %eax
	subl	$1, %edi
	jne	.L4
.L2:
	popl	%ebx
	popl	%esi
	popl	%edi
	ret
	.size	ncopy, .-ncopy
	.section	.text.startup,"ax",@progbits
	.p2align 4,,15
	.globl	main
	.type	main, @function
main:
	xorl	%eax, %eax
	xorl	%ecx, %ecx
	.p2align 4,,7
	.p2align 3
.L10:
	movl	src(%eax), %edx
	testl	%edx, %edx
	movl	%edx, dst(%eax)
	setg	%dl
	addl	$4, %eax
	movzbl	%dl, %edx
	addl	%edx, %ecx
	cmpl	$32, %eax
	jne	.L10
	movl	%ecx, count
	ret
	.size	main, .-main
	.globl	count
	.data
	.align 4
	.type	count, @object
	.size	count, 4
count:
	.long	-1
	.globl	dst
	.align 32
	.type	dst, @object
	.size	dst, 32
dst:
	.long	-1
	.long	-1
	.long	-1
	.long	-1
	.long	-1
	.long	-1
	.long	-1
	.long	-1
	.globl	src
	.align 32
	.type	src, @object
	.size	src, 32
src:
	.long	0
	.long	1
	.long	2
	.long	3
	.long	4
	.long	5
	.long	6
	.long	7
	.ident	"GCC: (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3"
	.section	.note.GNU-stack,"",@progbits
