/**
 * @file
 * libavformat AVIOContext API example.
 *
 * Make libavformat demuxer access media content through a custom
 * AVIOContext read callback.
 * @example avio_reading.c
 */

// 总体流程：
// 1）文件内容读入内存buffer中
// 2）由buffer创建AVIOContext
// 3）由AVIOContext创建AVFormatContext进行后序操作

#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavformat/avio.h>
#include <libavutil/file.h>

struct buffer_data
{
    uint8_t *ptr; //文件中对应位置指针
    size_t size;  ///文件当前指针到末尾数据大小
};
//将文件中数据拷贝至缓冲区，同时文件指针位置偏移，数据大小改变
static int read_packet(void *opaque, uint8_t *buf, int buf_size)
{
    struct buffer_data *bd = (struct buffer_data *)opaque;
    buf_size = FFMIN(buf_size, bd->size);
    printf("ptr:%p size:%u\n", bd->ptr, bd->size);
    /* copy internal buffer data to buf */
    memcpy(buf, bd->ptr, buf_size);
    bd->ptr += buf_size;
    bd->size -= buf_size;
    return buf_size;
}

int main(int argc, char *argv[])
{
    AVFormatContext *fmt_ctx = NULL;
    AVIOContext *avio_ctx = NULL;

    uint8_t *buffer = NULL;
    size_t buffer_size;
    struct buffer_data bd = {0};

    uint8_t *avio_ctx_buffer = NULL;
    size_t avio_ctx_buffer_size = 4096;

    const char *input_filename = "test.mkv";
    int ret = 0;

    //类似于UNIX下的mmap函数所实现的功能，返回文件开始指针，文件大小
    ret = av_file_map(input_filename, &buffer, &buffer_size, 0, NULL);
    if (ret < 0)
    {
        printf("av_file_map Err:%d\n", ret);
        goto end;
    }

    bd.ptr = buffer;
    bd.size = buffer_size;
    //初始化文件格式的结构体,就是分配内存,以后获取或设置编码格式都可以用这结构体管理，应该是当中的成员
    if (!(fmt_ctx = avformat_alloc_context()))
    {
        ret = AVERROR(ENOMEM);
        goto end;
    }

    //分配内存，可以自己设置缓冲大小
    if (!(avio_ctx_buffer = (uint8_t *)av_malloc(avio_ctx_buffer_size)))
    {
        ret = AVERROR(ENOMEM);
        goto end;
    }

    // 创建AVIOContext
    if (!(avio_ctx = avio_alloc_context(avio_ctx_buffer, avio_ctx_buffer_size, 0,
                                        &bd, &read_packet, NULL, NULL)))
    {
        ret = AVERROR(ENOMEM);
        goto end;
    }

    fmt_ctx->pb = avio_ctx;
    // 媒体打开函数
    ret = avformat_open_input(&fmt_ctx, NULL, NULL, NULL); 
    if (ret < 0)
    {
        printf("Open Err\n");
        goto end;
    }
    // 获取视频流信息
    ret = avformat_find_stream_info(fmt_ctx, NULL);
    if (ret < 0)
    {
        printf("Could not find stream information\n");
        goto end;
    }
    av_dump_format(fmt_ctx, 0, input_filename, 0);

end:
    avformat_close_input(&fmt_ctx);
    if (avio_ctx)
    {
        av_freep(&avio_ctx->buffer);
        av_freep(&avio_ctx);
    }
    av_file_unmap(buffer, buffer_size);
    printf("RET:%d\n", ret);
    system("PAUSE");
    return ret;
}
