#pragma once 
#include <string> 
#include <iostream>
using namespace std; 
class VideoStreamEngine {
public:
    explicit VideoStreamEngine(const string &source);
    void start(); 
    void stop(); 

    bool is_running() const; 
    string source() const; 
private: 
    string source_; 
    bool running_; 
};
