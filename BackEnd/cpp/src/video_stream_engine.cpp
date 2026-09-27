#include "video_stream_engine.hpp"
#include <iostream>
using namespace std; 
VideoStreamEngine::VideoStreamEngine(const string& source): source_(source), running_(false){
    //Minh Cute
}
void VideoStreamEngine::start() {
    if (running_) return; 
    running_ = true; 
    cout << "[VideoStreamEngine] Started Camera " << source_ << endl;
}

void VideoStreamEngine::stop() {
    if (!running_) {
        return;
    }

    running_ = false;

    cout << "[VideoStreamEngine] Stopped" << endl;
}

bool VideoStreamEngine::is_running() const {
    return running_;
}

string VideoStreamEngine::source() const {
    return source_;
}
