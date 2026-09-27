#include <pybind11/pybind11.h>
#include "video_stream_engine.hpp"

namespace py = pybind11; 
PYBIND11_MODULE(_video_stream, m) {
    m.doc() = "Cpp real-time video streaming engine"; 
    py::class_<VideoStreamEngine>(m, "VideoStreamEngine")
        .def(
            py::init<const std::string&>(), 
            py::arg("source")
        )
        .def(
            "start",
            &VideoStreamEngine::start
        )
        .def(
            "stop", 
            &VideoStreamEngine::stop
        )
        .def_property_readonly(
            "is_running", 
            &VideoStreamEngine::is_running
        )
        .def_property_readonly(
            "source",
            &VideoStreamEngine::source
        );
}
