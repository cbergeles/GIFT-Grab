#include "opencv_video_target.h"

namespace gg
{

VideoTargetOpenCV::VideoTargetOpenCV(const std::string fourcc)
{
    if (fourcc != "XVID") // currently only XviD supported
    {
        std::string msg;
        msg.append("FOURCC ")
           .append(fourcc)
           .append(" not supported");
        throw VideoTargetError(msg);
    }
    else
        _fourcc = fourcc;
}

void VideoTargetOpenCV::init(const std::string filepath, const float fps)
{
    if (fps <= 0)
        throw VideoTargetError("Negative fps does not make sense");

    if (filepath.length() <= 0)
        throw VideoTargetError("File path cannot be an empty string");

    _filepath = filepath;
    _fps = fps;
}

void VideoTargetOpenCV::append(const VideoFrame_BGRA & frame)
{
    if (not _writer.isOpened())
    {
        const char * buffer = _fourcc.c_str();
        int ex = CV_FOURCC(buffer[0],
                           buffer[1],
                           buffer[2],
                           buffer[3]);
        cv::Size size(frame.cols(),     // width
                      frame.rows());    // height
        _buffer_bgr = cv::Mat::zeros(frame.rows(), frame.cols(),
                                     CV_8UC3);

        try
        {
            _writer.open(_filepath, ex, _fps, size, true);
        }
        catch (std::exception & e)
        {
            throw VideoTargetError(e.what());
        }

        if (not _writer.isOpened())
        {
            std::string msg;
            msg.append("File ")
               .append(_filepath)
               .append(" could not be opened");
            throw VideoTargetError(msg);
        }
    }

    try
    {
        // TODO - performance, i.e. copy!
        cv::Mat cv_frame_bgra(frame.rows(), frame.cols(),
                              CV_8UC4,
                              const_cast<unsigned char *>(frame.data()));
        cv::cvtColor(cv_frame_bgra, _buffer_bgr, CV_BGRA2BGR);

        _writer << _buffer_bgr;
    }
    catch (std::exception & e)
    {
        throw VideoTargetError(e.what());
    }
}

void VideoTargetOpenCV::finalise()
{
    if (_writer.isOpened())
    {
        try
        {
            _writer.release();
        }
        catch (std::exception & e)
        {
            throw VideoTargetError(e.what());
        }

        _buffer_bgr.deallocate();
    }
}

}
