// 2.给你一个字符串s，找到s中最长的回文字串。

#include <iostream>
#include <string>
#include <vector>

using namespace std;

// 函数声明
string longestHuiwen(string s);
int CenterExpand(const string& s, int left, int right);

// 主函数
int main() {
    // 示例 1
    string s1 = "babad";
    cout << "示例1结果: " << longestHuiwen(s1) << "\n"; // 输出 "bab" 或 "aba"

    // 示例 2
    string s2 = "cbbd";
    cout << "示例2结果: " << longestHuiwen(s2) << "\n"; // 输出 "bb"

    return 0;
}

// 中心扩展法
string longestHuiwen(string s) {
    if (s.empty()) return "";

    int start = 0, end = 0; // 记录最长回文的起始和结束位置
    for (int i = 0; i < s.length(); ++i) {
        // 奇数长度回文（中心为单个字符）
        int len1 = CenterExpand(s, i, i);
        // 偶数长度回文（中心为两个字符）
        int len2 = CenterExpand(s, i, i + 1);
        int maxLen = max(len1, len2); // 取最大长度

        // 更新起始和结束位置
        if (maxLen > end - start) {
            start = i - (maxLen - 1) / 2;
            end = i + maxLen / 2;
        }
    }
    return s.substr(start, end - start + 1);
}

// 中心扩展函数
int CenterExpand(const string& s, int left, int right) {
    while (left >= 0 && right < s.length() && s[left] == s[right]) {
        --left;
        ++right;
    }
    // 返回实际回文长度（因为最后一步超出边界，需减去 2）
    return right - left - 1;
}