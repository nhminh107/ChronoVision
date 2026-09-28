cmake_minimum_required(VERSION 3.18)

project(ChronoVisionVideoStream LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(PYBIND11_FINDPYTHON ON)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

execute_process(
    COMMAND "${Python_EXECUTABLE}" -m pybind11 --cmakedir
    RESULT_VARIABLE PYBIND11_DISCOVERY_RESULT
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
)

if(NOT PYBIND11_DISCOVERY_RESULT EQUAL 0)
    message(FATAL_ERROR
        "pybind11 is unavailable in the selected Python environment: "
        "${Python_EXECUTABLE}. Select an environment containing pybind11 "
        "with -DPython_EXECUTABLE=/path/to/python."
    )
endif()

find_package(pybind11 CONFIG REQUIRED HINTS "${PYBIND11_CMAKE_DIR}")
find_package(PkgConfig REQUIRED)
pkg_check_modules(FFMPEG REQUIRED IMPORTED_TARGET
    libavformat
    libavcodec
    libavutil
)

pybind11_add_module(_video_stream
    src/bindings.cpp
    src/video_stream_engine.cpp
    src/ffmpeg_decoder.cpp
)

target_include_directories(_video_stream PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/include"
)
target_compile_features(_video_stream PRIVATE cxx_std_17)
target_link_libraries(_video_stream PRIVATE PkgConfig::FFMPEG)
set_target_properties(_video_stream PROPERTIES CXX_EXTENSIONS OFF)

install(TARGETS _video_stream
    LIBRARY DESTINATION visual_memory
    RUNTIME DESTINATION visual_memory
)
