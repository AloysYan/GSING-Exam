#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>

using namespace std;

#define MAX(a, b) ((a) > (b) ? (a) : (b))

const int N = 50;
int n, m;
int f[N * 2 + 5][N + 5][N + 5];
int a[N + 5][N + 5];

int main() {
    cin >> n >> m;
    
    // 读取二维数组 a
    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= m; ++j) {
            cin >> a[i][j];
        }
    }
    
    // 初始化 f 数组为 -1
    memset(f, -1, sizeof(f));
    f[2][1][1] = 0;
    
    // 动态规划的主体
    for (int i = 3; i < n + m; ++i) {
        for (int j = 1; j < n; ++j) {
            for (int k = j + 1; k <= n; ++k) {
                // 执行状态转移
                f[i][j][k] = MAX(f[i][j][k], f[i - 1][j - 1][k - 1]);
                f[i][j][k] = MAX(f[i][j][k], f[i - 1][j][k - 1]);
                f[i][j][k] = MAX(f[i][j][k], f[i - 1][j - 1][k]);
                f[i][j][k] = MAX(f[i][j][k], f[i - 1][j][k]);
                
                if (f[i][j][k] == -1) continue;  // 如果仍然是 -1，则不能更新
                
                // 累加好感度
                f[i][j][k] += a[j][i - j] + a[k][i - k];
            }
        }
    }
    
    cout << f[n + m - 1][n - 1][n] << endl;  // 输出结果
    
    return 0;
}
