#pragma once

#include <cstdint>
#include <string>

extern "C" {
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/avutil.h>
}

struct FrameInfo {
    int width = 0;
    int height = 0;

    int64_t pts = 0;
    double timestamp_sec = 0.0;

    int pixel_format = -1;
};


class FFmpegDecoder {
public:
    explicit FFmpegDecoder(const std::string& source);

    ~FFmpegDecoder();

    void open();
    void close();

    bool is_open() const;

    bool read_frame(FrameInfo& info);

    int width() const;
    int height() const;

    double fps() const;

private:
    std::string source_;

    AVFormatContext* format_context_;
    AVCodecContext* codec_context_;

    AVPacket* packet_;
    AVFrame* frame_;

    int video_stream_index_;

    bool opened_;
};