cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

message(STATUS "Conan CMake Wrapper")
include("conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

set(absl_DIR "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
message("absl_DIR ${absl_DIR}")
add_subdirectory("source_subfolder")
