#include "ffmpeg_decoder.hpp"

#include <stdexcept>
#include <string>

extern "C" {
#include <libavutil/error.h>
}

namespace {

std::string ffmpeg_error_string(int error_code) {
    char buffer[AV_ERROR_MAX_STRING_SIZE];

    av_strerror(
        error_code,
        buffer,
        sizeof(buffer)
    );

    return std::string(buffer);
}

}

FFmpegDecoder::FFmpegDecoder(const std::string& source)
    : source_(source),
      format_context_(nullptr),
      codec_context_(nullptr),
      packet_(nullptr),
      frame_(nullptr),
      video_stream_index_(-1),
      opened_(false) {
}
FFmpegDecoder::~FFmpegDecoder() {
    close();
}

void FFmpegDecoder::open() {
    if (opened_) return; 
    int ret; 

    ret = avformat_open_input(
        &format_context_, 
        source_.c_str(),
        nullptr,
        nullptr
    );

    if (ret < 0) {
        throw std::runtime_error(
            "Failed to open input: " + 
            ffmpeg_error_string(ret)
        ); 
    }
    ret = avformat_find_stream_info(
        format_context_, 
        nullptr
    ); 
    if (ret < 0) {
        throw std::runtime_error(
            "Failed to find stream info: " + ffmpeg_error_string(ret)
        ); 
    }

    const AVCodec* decoder = nullptr; 
    video_stream_index_ = av_find_best_stream(
        format_context_, AVMEDIA_TYPE_VIDEO, -1, -1, &decoder, 0
    ); 

    if (video_stream_index_ < 0) {
        throw std::runtime_error(
            "No video stream found"
        ); 
    }

    AVStream* video_stream = format_context_->streams[video_stream_index_];
    codec_context_ = avcodec_alloc_context3(decoder);

    if (!codec_context_) {
        throw std::runtime_error(
            "Failed to allocate codec context"
        );
    }
        ret = avcodec_parameters_to_context(
        codec_context_,
        video_stream->codecpar
    );

    if (ret < 0) {
        throw std::runtime_error(
            "Failed to copy codec parameters: " +
            ffmpeg_error_string(ret)
        );
    }
    ret = avcodec_open2(
        codec_context_,
        decoder,
        nullptr
    );

    if (ret < 0) {
        throw std::runtime_error(
            "Failed to open decoder: " +
            ffmpeg_error_string(ret)
        );
    }
    packet_ = av_packet_alloc();
    frame_ = av_frame_alloc();

    if (!packet_ || !frame_) {
        throw std::runtime_error(
            "Failed to allocate packet/frame"
        );
    }

    opened_ = true; 
}

bool FFmpegDecoder::read_frame(FrameInfo& info) {
    if (!opened_) {
        throw std::runtime_error(
            "Decoder is not open"
        );
    }

    while (av_read_frame(
        format_context_,
        packet_
    ) >= 0) {

        if (
            packet_->stream_index
            != video_stream_index_
        ) {
            av_packet_unref(packet_);
            continue;
        }

        int ret = avcodec_send_packet(
            codec_context_,
            packet_
        );

        av_packet_unref(packet_);

        if (ret < 0) {
            continue;
        }

        ret = avcodec_receive_frame(
            codec_context_,
            frame_
        );

        if (ret == AVERROR(EAGAIN)) {
            continue;
        }

        if (ret < 0) {
            continue;
        }

        info.width = frame_->width;
        info.height = frame_->height;

        info.pixel_format = frame_->format;

        int64_t pts =
            frame_->best_effort_timestamp;

        info.pts = pts;

        AVStream* stream =
            format_context_->streams[
                video_stream_index_
            ];

        if (pts != AV_NOPTS_VALUE) {
            info.timestamp_sec =
                pts * av_q2d(
                    stream->time_base
                );
        } else {
            info.timestamp_sec = -1.0;
        }

        return true;
    }

    return false;
}
bool FFmpegDecoder::is_open() const {
    return opened_;
}


int FFmpegDecoder::width() const {
    if (!codec_context_) {
        return 0;
    }

    return codec_context_->width;
}


int FFmpegDecoder::height() const {
    if (!codec_context_) {
        return 0;
    }

    return codec_context_->height;
}
void FFmpegDecoder::close() {
    if (frame_) {
        av_frame_free(&frame_);
    }

    if (packet_) {
        av_packet_free(&packet_);
    }

    if (codec_context_) {
        avcodec_free_context(
            &codec_context_
        );
    }

    if (format_context_) {
        avformat_close_input(
            &format_context_
        );
    }

    video_stream_index_ = -1;
    opened_ = false;
}