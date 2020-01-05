	.file	"len1.c"
	.text
	.p2align 4,,15
	.globl	len1
	.type	len1, @function
len1:
	movl	4(%esp), %edx
	xorl	%eax, %eax
	movl	(%edx), %ecx
	testl	%ecx, %ecx
	je	.L2
	.p2align 4,,7
	.p2align 3
.L3:
	addl	$1, %eax
	movl	(%edx,%eax,4), %ecx
	testl	%ecx, %ecx
	jne	.L3
.L2:
	rep
	ret
	.size	len1, .-len1
	.section	.text.startup,"ax",@progbits
	.p2align 4,,15
	.globl	main
	.type	main, @function
main:
	movl	List, %ecx
	xorl	%eax, %eax
	testl	%ecx, %ecx
	je	.L8
.L9:
	addl	$1, %eax
	movl	List(,%eax,4), %edx
	testl	%edx, %edx
	jne	.L9
.L8:
	movl	%eax, thelength
	xorl	%eax, %eax
	ret
	.size	main, .-main
	.globl	thelength
	.data
	.align 4
	.type	thelength, @object
	.size	thelength, 4
thelength:
	.long	-1
	.globl	List
	.align 4
	.type	List, @object
	.size	List, 20
List:
	.long	1
	.long	2
	.long	3
	.long	4
	.long	0
	.ident	"GCC: (Ubuntu/Linaro 4.6.4-1ubuntu1~12.04) 4.6.4"
	.section	.note.GNU-stack,"",@progbits
