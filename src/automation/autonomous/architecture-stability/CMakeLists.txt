cmake_minimum_required(VERSION 3.8)
project(autonomy_core)

# 設定 C++ 標準
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 尋找依賴項
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

# 創建執行檔
add_executable(flight_controller flight_controller.cpp)
ament_target_dependencies(flight_controller
  rclcpp
  geometry_msgs
  sensor_msgs
)

# 安裝目標
install(TARGETS
  flight_controller
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
