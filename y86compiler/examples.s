	.file	"examples.c"
	.text
	.p2align 4,,15
	.globl	sum_list
	.type	sum_list, @function
sum_list:
	movl	4(%esp), %edx
	xorl	%eax, %eax
	testl	%edx, %edx
	je	.L2
	.p2align 4,,7
	.p2align 3
.L3:
	addl	(%edx), %eax
	movl	4(%edx), %edx
	testl	%edx, %edx
	jne	.L3
.L2:
	rep
	ret
	.size	sum_list, .-sum_list
	.p2align 4,,15
	.globl	rsum_list
	.type	rsum_list, @function
rsum_list:
	movl	4(%esp), %edx
	xorl	%eax, %eax
	testl	%edx, %edx
	je	.L8
	.p2align 4,,7
	.p2align 3
.L9:
	movl	(%edx), %ecx
	movl	4(%edx), %edx
	addl	%ecx, %eax
	testl	%edx, %edx
	jne	.L9
.L8:
	rep
	ret
	.size	rsum_list, .-rsum_list
	.p2align 4,,15
	.globl	copy_block
	.type	copy_block, @function
copy_block:
	pushl	%esi
	xorl	%eax, %eax
	pushl	%ebx
	movl	20(%esp), %edx
	movl	12(%esp), %ebx
	movl	16(%esp), %ecx
	testl	%edx, %edx
	jle	.L13
	.p2align 4,,7
	.p2align 3
.L14:
	movl	(%ebx), %esi
	addl	$4, %ebx
	movl	%esi, (%ecx)
	xorl	%esi, %eax
	addl	$4, %ecx
	subl	$1, %edx
	jne	.L14
.L13:
	popl	%ebx
	popl	%esi
	ret
	.size	copy_block, .-copy_block
	.section	.text.startup,"ax",@progbits
	.p2align 4,,15
	.globl	main
	.type	main, @function
main:
	movl	list, %eax
	xorl	%edx, %edx
	testl	%eax, %eax
	je	.L18
	.p2align 4,,7
	.p2align 3
.L19:
	addl	(%eax), %edx
	movl	4(%eax), %eax
	testl	%eax, %eax
	jne	.L19
.L18:
	movl	%edx, thesum
	xorl	%eax, %eax
	ret
	.size	main, .-main
	.globl	list
	.data
	.align 4
	.type	list, @object
	.size	list, 4
list:
	.long	ele1
	.globl	ele1
	.align 4
	.type	ele1, @object
	.size	ele1, 8
ele1:
	.long	10
	.long	ele2
	.globl	ele2
	.align 4
	.type	ele2, @object
	.size	ele2, 8
ele2:
	.long	176
	.long	ele3
	.globl	ele3
	.align 4
	.type	ele3, @object
	.size	ele3, 8
ele3:
	.long	3072
	.long	0
	.globl	thesum
	.align 4
	.type	thesum, @object
	.size	thesum, 4
thesum:
	.long	-1
	.ident	"GCC: (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3"
	.section	.note.GNU-stack,"",@progbits
