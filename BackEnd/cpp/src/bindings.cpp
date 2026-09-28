#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "video_stream_engine.hpp"
#include "ffmpeg_decoder.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_video_stream, m) {
    m.doc() =
        "C++ video stream engine";

    py::class_<FrameInfo>(
        m,
        "FrameInfo"
    )
        .def_readonly(
            "width",
            &FrameInfo::width
        )
        .def_readonly(
            "height",
            &FrameInfo::height
        )
        .def_readonly(
            "pts",
            &FrameInfo::pts
        )
        .def_readonly(
            "timestamp_sec",
            &FrameInfo::timestamp_sec
        )
        .def_readonly(
            "pixel_format",
            &FrameInfo::pixel_format
        );


    py::class_<FFmpegDecoder>(
        m,
        "FFmpegDecoder"
    )
        .def(
            py::init<const std::string&>()
        )

        .def(
            "open",
            &FFmpegDecoder::open
        )

        .def(
            "close",
            &FFmpegDecoder::close
        )

        .def_property_readonly(
            "is_open",
            &FFmpegDecoder::is_open
        )

        .def_property_readonly(
            "width",
            &FFmpegDecoder::width
        )

        .def_property_readonly(
            "height",
            &FFmpegDecoder::height
        )

        .def_property_readonly(
            "fps",
            &FFmpegDecoder::fps
        )

        .def(
            "read_frame",
            [](FFmpegDecoder& decoder)
                -> py::object {

                FrameInfo info;

                if (!decoder.read_frame(info)) {
                    return py::none();
                }

                return py::cast(info);
            }
        );


    py::class_<VideoStreamEngine>(
        m,
        "VideoStreamEngine"
    )
        .def(
            py::init<const std::string&>()
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