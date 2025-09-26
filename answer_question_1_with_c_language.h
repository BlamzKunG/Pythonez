#include <stdio.h>
#include <limits.h>

int main() {
    int n;
    
    // รับจำนวนที่เป็นลิสต์ของตัวเลข
    while (scanf("%d", &n) != EOF) {
        int numbers[n];
        
        // อ่านตัวเลขในลิสต์
        for (int i = 0; i < n; i++) {
            scanf("%d", &numbers[i]);
        }

        // ค้นหาค่ามากสุดและน้อยสุด
        int min = INT_MAX, max = INT_MIN;
        for (int i = 0; i < n; i++) {
            if (numbers[i] < min) min = numbers[i];
            if (numbers[i] > max) max = numbers[i];
        }

        // หาผลรวมของตัวเลขที่เหลือหลังจากตัดค่ามากสุดและน้อยสุด
        int sum = 0, count = 0;
        for (int i = 0; i < n; i++) {
            if (numbers[i] != min && numbers[i] != max) {
                sum += numbers[i];
                count++;
            }
        }

        // คำนวณค่าเฉลี่ย
        if (count > 0) {
            printf("%.2f\n", (float)sum / count);
        } else {
            printf("Error: No numbers left after removal\n");
        }
    }

    return 0;
}
