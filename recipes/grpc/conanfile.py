import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version
from conans.tools import Version


_SOURCE_URL='https://github.com/grpc/grpc/archive/v{0}.tar.gz'

class gRPCConan(ConanFile):
    name = "grpc"
    description = "gRPC - A high-performance, open source universal RPC framework"
    topics = ("conan", "protobuf", "grpc", "grpc-gencode", "serialization", "rpc")
    url = "https://github.com/kumokami/conan-index"
    homepage = "https://grpc.io"
    license = "Apache License v2.0"
    exports_sources = ["CMakeLists.txt", "cmake/abslConfig.cmake"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "with_codegen": [True, False], 
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "with_codegen": True,
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

    def requirements(self):
        self.requires("protobuf/3.9.1")
        self.requires("openssl/1.1.1f")
        self.requires("zlib/1.2.11")
        self.requires("c-ares/1.15.0")
        self.requires("abseil/20200205")

    def build_requirements(self):
        self.build_requires("protoc_installer/3.9.1@bincrafters/stable")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["gRPC_BACKWARDS_COMPATIBILITY_MOD"] = True

        cmake.definitions["gRPC_PROTOBUF_PROVIDER"] = "package"
        cmake.definitions["Protobuf_USE_STATIC_LIBS"] = True

        cmake.definitions["gRPC_SSL_PROVIDER"] = "package"
        cmake.definitions["gRPC_ZLIB_PROVIDER"] = "package"
        cmake.definitions["gRPC_ABSL_PROVIDER"] = "package"

        cmake.definitions["gRPC_CARES_PROVIDER"] = "conan"
        cmake.definitions["_gRPC_CARES_LIBRARIES"] = "CONAN_PKG::c-ares"

        cmake.definitions["gRPC_BUILD_CODEGEN"] = self.options.with_codegen
        cmake.definitions["gRPC_BUILD_GRPC_CPP_PLUGIN"] = True

        cmake.definitions["gRPC_INSTALL"] = True

        #Disable no useful codegen
        DISABLE_PLUGINS_LIST = ["CSHARP", "NODE", "OBJECTIVE_C", "PHP", "PYTHON", "RUBY"]
        for plugin_name in DISABLE_PLUGINS_LIST:
            cmake.definitions[f"gRPC_BUILD_GRPC_{plugin_name}_PLUGIN"] = "OFF"

        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
       
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

    def package_info(self):
        self.cpp_info.libs = [
            'grpcpp_channelz',
            'grpc_unsecure',
            'grpc_plugin_support',
            'grpc_cronet',
            'grpc++_unsecure',
            'grpc++_reflection',
            'grpc++_error_details',
            'grpc++_alts',
            'grpc++',
            'grpc',
            'gpr',
            'address_sorting', 
            'upb'
        ]

        self.cpp_info.names["cmake_find_package"] = "grpc"
        self.cpp_info.names["cmake_find_package_multi"] = "grpc"