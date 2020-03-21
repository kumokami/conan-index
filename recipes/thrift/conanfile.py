import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version
from conans.tools import Version

_SOURCE_URL='https://mirrors.tuna.tsinghua.edu.cn/apache/thrift/{0}/thrift-{0}.tar.gz'

class ThriftConan(ConanFile):
    name = "thrift"
    description = "Thrift - Apache Thrift RPC framework"
    topics = ("conan", "thrift", "thrift-compiler", "serialization", "rpc")
    url = "https://github.com/kumokami/conan-index"
    homepage = "https://thrift.apache.org"
    license = "Apache License v2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    short_paths = True
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "with_cpp": [True, False], 
        "with_zlib": [True, False], 
        "with_libevent": [True, False], 
        "with_openssl": [True, False], 
        "with_boost_threads": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "with_cpp": True,
        "with_zlib": False,
        "with_openssl": True,
        "with_libevent": False,
        "with_boost_threads": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(url=_SOURCE_URL.format(self.version))
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC

        if not self.options.with_cpp:
            del self.options.with_libevent
            del self.options.with_openssl

        if self.version > "0.13.0":
            del self.options.with_boost_threads

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_cpp:
            self.requires("boost/1.72.0")
            if self.options.with_openssl:
                self.requires("openssl/1.1.1d")
            if self.options.with_libevent:
                self.requires("libevent/2.1.11")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_COMPILER"] = False
        cmake.definitions["WITH_STATIC_LIB"] = not self.options.shared
        cmake.definitions["WITH_SHARED_LIB"] = self.options.shared
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        cmake.definitions["BUILD_LIBRARIES"] = True
        cmake.definitions["WITH_CPP"] = self.options.with_cpp
        cmake.definitions["WITH_BOOSTTHREADS"] = self.options.with_boost_threads

        if self.options.with_cpp:
            cmake.definitions["WITH_QT5"] = False
            cmake.definitions["WITH_ZLIB"] = self.options.with_zlib
            cmake.definitions["WITH_LIBEVENT"] = self.options.with_libevent
            cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
       
        turnOffDefintions = [
            "WITH_C_GLIB"
            "BUILD_JAVA",
            "BUILD_JAVASCRIPT",
            "BUILD_NODEJS",
            "BUILD_PYTHON",
            "BUILD_HASKELL",
            "BUILD_AS3",
            "BUILD_TESTING",
            "BUILD_TUTORIALS"
        ]
        for VAR in turnOffDefintions:
            cmake.definitions[VAR] = False

        if self.settings.compiler == "Visual Studio":
            cmake.definitions["WITH_MT"] = "MT" in self.settings.compiler.runtime
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os != "Windows":
            self.copy("config.h", dst="include/thrift", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.sort(reverse=True)

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.defines = ["THRIFT_STATIC_DEFINE"]

        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.build_modules = ["lib/cmake"]

        self.cpp_info.names["cmake_find_package"] = "thrift"
        self.cpp_info.names["cmake_find_package_multi"] = "thrift"