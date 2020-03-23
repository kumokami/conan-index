# MIT License
# 
# Copyright (c) 2020 KumoKami
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

find_program(THRIFT_EXECUTABLE NAMES thrift thrift.exe NO_DEFAULT_PATH
    PATHS "${CONAN_BIN_DIRS_THRIFT_COMPILER}"
)

if(THRIFT_EXECUTABLE)
    message("Found thrift compiler: ${THRIFT_EXECUTABLE}")
endif()

function(compile_thrift)
    if(NOT THRIFT_EXECUTABLE)
        message(FATAL_ERROR "Thrift compiler not found")
    endif()

    cmake_parse_arguments(THRIFT "" "NAME" "FILES;SERVICES" ${ARGV})

    set(THIRFT_OUTDIR ${CMAKE_CURRENT_BINARY_DIR}/gen-cpp)
    foreach(FILENAME ${THRIFT_FILES})
        get_filename_component(THRIFT_FILE_NAME ${FILENAME} NAME_WE)
        list(APPEND ${THRIFT_NAME}_SOURCES ${THIRFT_OUTDIR}/${THRIFT_FILE_NAME}_constants.cpp)
        list(APPEND ${THRIFT_NAME}_SOURCES ${THIRFT_OUTDIR}/${THRIFT_FILE_NAME}_constants.h)
        list(APPEND ${THRIFT_NAME}_SOURCES ${THIRFT_OUTDIR}/${THRIFT_FILE_NAME}_types.cpp)
        list(APPEND ${THRIFT_NAME}_SOURCES ${THIRFT_OUTDIR}/${THRIFT_FILE_NAME}_types.h)
        list(APPEND ${THRIFT_NAME}_SOURCES ${THIRFT_OUTDIR}/${THRIFT_FILE_NAME}_types.tcc)
        list(APPEND ${THRIFT_NAME}_COMMANDS COMMAND ${THRIFT_EXECUTABLE}
                -o ${CMAKE_CURRENT_BINARY_DIR}
                -gen cpp:no_client_completion=true,no_default_operators=true,templates=true ${FILENAME}
        )
    endforeach()
    foreach(SERVICE ${THRIFT_SERVICES})
        list(APPEND ${THRIFT_NAME}_SOURCES ${THIRFT_OUTDIR}/${SERVICE}.cpp)
        list(APPEND ${THRIFT_NAME}_SOURCES ${THIRFT_OUTDIR}/${SERVICE}.tcc)
        list(APPEND ${THRIFT_NAME}_SOURCES ${THIRFT_OUTDIR}/${SERVICE}.h)
    endforeach()

    add_custom_command(OUTPUT ${${THRIFT_NAME}_SOURCES}
        DEPENDS ${THRIFT_FILES}
        COMMAND ${CMAKE_COMMAND} 
            -E remove_directory ${THIRFT_OUTDIR}
        ${${THRIFT_NAME}_COMMANDS}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )

    set(${THRIFT_NAME}_SOURCES ${${THRIFT_NAME}_SOURCES} PARENT_SCOPE)
endfunction()