import os
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

_SOURCE_URL='https://mirrors.tuna.tsinghua.edu.cn/apache/thrift/{0}/thrift-{0}.tar.gz'
_WIN_BIN_URL='https://mirrors.tuna.tsinghua.edu.cn/apache/thrift/{0}/thrift-{0}.exe'

class ThriftConan(ConanFile):
    name = "thrift-compiler"
    description = "Thrift - Apache Thrift RPC framework"
    topics = ("conan", "thrift", "thrift-compiler", "serialization", "rpc")
    url = "https://github.com/kumokami/conan-index"
    homepage = "https://thrift.apache.org"
    license = "Apache License v2.0"
    exports_sources = ["CMakeLists.txt", "FindThriftCompiler.cmake"]
    generators = "cmake"
    short_paths = True
    settings = "compiler", "arch", "os_build", "arch_build"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        if self.settings.os_build != "Windows":
            tools.get(url=_SOURCE_URL.format(self.version))
            extracted_folder = "thrift-" + self.version
            os.rename(extracted_folder, self._source_subfolder)

    def requirements(self):
        self.requires("boost/1.72.0", private=True)

    def configure(self):
        pass

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_COMPILER"] = True
        cmake.definitions["CMAKE_BUILD_TYPE"] = "Release"
        cmake.definitions["BUILD_LIBRARIES"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        if self.settings.os_build != "Windows":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            tools.download(filename='thrift.exe', url=_WIN_BIN_URL.format(self.version))

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os_build != "Windows":
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        else:
            self.copy("thrift.exe", dst="bin")
        
        self.copy("FindThriftCompiler.cmake")
        
    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.arch
        self.info.include_build_settings()

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))