'''
1.给定一个整数数组 nums 和⼀个整数目标值 target ，请你在该数组中找出
和为目标值 target的那两个整数 ，并返回它们的数组下标。
你可以假设每种输⼊只会对应⼀个答案，并且你不能使⽤两次相同的元素。
你可以按任意顺序返回答案。
'''
# 解法：使用哈希表存储已经遍历过的数字及其索引，遍历数组时检查当前数字的补数是否在哈希表中。
def two_sum(nums, target):
    num_to_index = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_to_index:
            return [num_to_index[complement], i]
        num_to_index[num] = i
    return []

# 示例 1
nums1 = [2, 7, 11, 15]
target1 = 9
print(two_sum(nums1, target1))  # 输出: [0, 1]

# 示例 2
nums2 = [3, 2, 4]
target2 = 6
print(two_sum(nums2, target2))  # 输出: [1, 2]

# 示例 3
nums3 = [3, 3]
target3 = 6
print(two_sum(nums3, target3))  # 输出: [0, 1]