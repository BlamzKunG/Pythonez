#include <stdio.h>

int main() {
    int n;
    
    // รับจำนวนที่เป็นลิสต์ของราคาหุ้น
    while (scanf("%d", &n) != EOF) {
        int prices[n];
        
        // อ่านราคาหุ้นในลิสต์
        for (int i = 0; i < n; i++) {
            scanf("%d", &prices[i]);
        }

        // หากำไรสูงสุดที่สามารถทำได้
        int min_price = prices[0];
        int max_profit = 0;

        for (int i = 1; i < n; i++) {
            int profit = prices[i] - min_price;
            if (profit > max_profit) {
                max_profit = profit;
            }
            if (prices[i] < min_price) {
                min_price = prices[i];
            }
        }

        // แสดงผลกำไรสูงสุด
        printf("%d\n", max_profit);
    }

    return 0;
}
