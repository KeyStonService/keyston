"""
範例應用程式 - 展示偵錯功能
Sample Application - Demonstrating Debug Features
"""

import time
from typing import List, Dict


class Calculator:
    """簡單的計算器類別"""
    
    def __init__(self):
        self.history: List[Dict] = []
    
    def add(self, a: float, b: float) -> float:
        """加法"""
        result = a + b
        self.history.append({
            'operation': 'add',
            'operands': [a, b],
            'result': result
        })
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """減法"""
        result = a - b
        self.history.append({
            'operation': 'subtract',
            'operands': [a, b],
            'result': result
        })
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """乘法"""
        result = a * b
        self.history.append({
            'operation': 'multiply',
            'operands': [a, b],
            'result': result
        })
        return result
    
    def divide(self, a: float, b: float) -> float:
        """除法"""
        # 這裡可能會發生 ZeroDivisionError
        # 設定斷點在這裡來檢查 b 的值
        if b == 0:
            raise ValueError("Cannot divide by zero")
        
        result = a / b
        self.history.append({
            'operation': 'divide',
            'operands': [a, b],
            'result': result
        })
        return result
    
    def get_history(self) -> List[Dict]:
        """取得計算歷史"""
        return self.history


def process_numbers(numbers: List[float]) -> Dict[str, float]:
    """處理數字列表"""
    # 設定斷點在這裡來檢查 numbers 的值
    if not numbers:
        return {'sum': 0, 'average': 0, 'max': 0, 'min': 0}
    
    total = sum(numbers)
    average = total / len(numbers)
    maximum = max(numbers)
    minimum = min(numbers)
    
    # 設定條件斷點：當 average > 50 時停止
    result = {
        'sum': total,
        'average': average,
        'max': maximum,
        'min': minimum
    }
    
    return result


def fibonacci(n: int) -> int:
    """計算費波那契數列"""
    # 設定斷點來觀察遞迴過程
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def demonstrate_errors():
    """展示常見錯誤"""
    print("\n=== 展示常見錯誤 ===")
    
    # 1. ZeroDivisionError
    try:
        calc = Calculator()
        result = calc.divide(10, 0)  # 設定斷點在這裡
    except ValueError as e:
        print(f"錯誤 1: {e}")
    
    # 2. IndexError
    try:
        numbers = [1, 2, 3]
        value = numbers[10]  # 設定斷點在這裡
    except IndexError as e:
        print(f"錯誤 2: {e}")
    
    # 3. KeyError
    try:
        data = {'name': 'John', 'age': 30}
        city = data['city']  # 設定斷點在這裡
    except KeyError as e:
        print(f"錯誤 3: {e}")
    
    # 4. TypeError
    try:
        result = "hello" + 5  # 設定斷點在這裡
    except TypeError as e:
        print(f"錯誤 4: {e}")


def main():
    """主程式"""
    print("=== MachineNativeOps 偵錯範例 ===\n")
    
    # 1. 基本計算
    print("1. 基本計算")
    calc = Calculator()
    
    # 設定斷點在這些行來觀察變數變化
    result1 = calc.add(10, 20)
    print(f"10 + 20 = {result1}")
    
    result2 = calc.multiply(5, 6)
    print(f"5 * 6 = {result2}")
    
    result3 = calc.divide(100, 4)
    print(f"100 / 4 = {result3}")
    
    # 2. 處理數字列表
    print("\n2. 處理數字列表")
    numbers = [10, 25, 30, 45, 60, 75]
    stats = process_numbers(numbers)
    print(f"統計資料: {stats}")
    
    # 3. 費波那契數列
    print("\n3. 費波那契數列")
    n = 8
    fib_result = fibonacci(n)
    print(f"fibonacci({n}) = {fib_result}")
    
    # 4. 展示錯誤處理
    demonstrate_errors()
    
    # 5. 顯示計算歷史
    print("\n5. 計算歷史")
    history = calc.get_history()
    for i, record in enumerate(history, 1):
        print(f"{i}. {record['operation']}: {record['operands']} = {record['result']}")
    
    print("\n=== 程式執行完成 ===")


if __name__ == "__main__":
    # 設定斷點在 main() 來開始偵錯
    main()