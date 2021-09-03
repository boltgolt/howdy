# Python bindings for the v4l2 userspace api

# Copyright (C) 1999-2009 the contributors

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Alternatively you can redistribute this file under the terms of the
# BSD license as stated below:

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 3. The names of its contributors may not be used to endorse or promote
#    products derived from this software without specific prior written
#    permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Python bindings for the v4l2 userspace api in Linux 2.6.34
"""

# see linux/videodev2.h

import ctypes


_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ  = 2


def _IOC(dir_, type_, nr, size):
    return (
        ctypes.c_int32(dir_ << _IOC_DIRSHIFT).value |
        ctypes.c_int32(ord(type_) << _IOC_TYPESHIFT).value |
        ctypes.c_int32(nr << _IOC_NRSHIFT).value |
        ctypes.c_int32(size << _IOC_SIZESHIFT).value)


def _IOC_TYPECHECK(t):
    return ctypes.sizeof(t)


def _IO(type_, nr):
    return _IOC(_IOC_NONE, type_, nr, 0)


def _IOW(type_, nr, size):
    return _IOC(_IOC_WRITE, type_, nr, _IOC_TYPECHECK(size))


def _IOR(type_, nr, size):
    return _IOC(_IOC_READ, type_, nr, _IOC_TYPECHECK(size))


def _IOWR(type_, nr, size):
    return _IOC(_IOC_READ | _IOC_WRITE, type_, nr, _IOC_TYPECHECK(size))


#
# type alias
#

enum = ctypes.c_uint
c_int = ctypes.c_int


#
# time
#

class timeval(ctypes.Structure):
    _fields_ = [
        ('secs', ctypes.c_long),
        ('usecs', ctypes.c_long),
    ]


#
# v4l2
#


VIDEO_MAX_FRAME = 32


VID_TYPE_CAPTURE = 1
VID_TYPE_TUNER = 2
VID_TYPE_TELETEXT = 4
VID_TYPE_OVERLAY = 8
VID_TYPE_CHROMAKEY = 16
VID_TYPE_CLIPPING = 32
VID_TYPE_FRAMERAM = 64
VID_TYPE_SCALES	= 128
VID_TYPE_MONOCHROME = 256
VID_TYPE_SUBCAPTURE = 512
VID_TYPE_MPEG_DECODER = 1024
VID_TYPE_MPEG_ENCODER = 2048
VID_TYPE_MJPEG_DECODER = 4096
VID_TYPE_MJPEG_ENCODER = 8192


def v4l2_fourcc(a, b, c, d):
    return ord(a) | (ord(b) << 8) | (ord(c) << 16) | (ord(d) << 24)


v4l2_field = enum
(
    V4L2_FIELD_ANY,
    V4L2_FIELD_NONE,
    V4L2_FIELD_TOP,
    V4L2_FIELD_BOTTOM,
    V4L2_FIELD_INTERLACED,
    V4L2_FIELD_SEQ_TB,
    V4L2_FIELD_SEQ_BT,
    V4L2_FIELD_ALTERNATE,
    V4L2_FIELD_INTERLACED_TB,
    V4L2_FIELD_INTERLACED_BT,
) = range(10)


def V4L2_FIELD_HAS_TOP(field):
    return (
	field == V4L2_FIELD_TOP or
	field == V4L2_FIELD_INTERLACED or
	field == V4L2_FIELD_INTERLACED_TB or
	field == V4L2_FIELD_INTERLACED_BT or
	field == V4L2_FIELD_SEQ_TB or
	field == V4L2_FIELD_SEQ_BT)


def V4L2_FIELD_HAS_BOTTOM(field):
    return (
        field == V4L2_FIELD_BOTTOM or
        field == V4L2_FIELD_INTERLACED or
        field == V4L2_FIELD_INTERLACED_TB or
        field == V4L2_FIELD_INTERLACED_BT or
        field == V4L2_FIELD_SEQ_TB or
        field == V4L2_FIELD_SEQ_BT)


def V4L2_FIELD_HAS_BOTH(field):
    return (
        field == V4L2_FIELD_INTERLACED or
        field == V4L2_FIELD_INTERLACED_TB or
        field == V4L2_FIELD_INTERLACED_BT or
        field == V4L2_FIELD_SEQ_TB or
        field == V4L2_FIELD_SEQ_BT)


v4l2_buf_type = enum
(
    V4L2_BUF_TYPE_VIDEO_CAPTURE,
    V4L2_BUF_TYPE_VIDEO_OUTPUT,
    V4L2_BUF_TYPE_VIDEO_OVERLAY,
    V4L2_BUF_TYPE_VBI_CAPTURE,
    V4L2_BUF_TYPE_VBI_OUTPUT,
    V4L2_BUF_TYPE_SLICED_VBI_CAPTURE,
    V4L2_BUF_TYPE_SLICED_VBI_OUTPUT,
    V4L2_BUF_TYPE_VIDEO_OUTPUT_OVERLAY,
    V4L2_BUF_TYPE_PRIVATE,
) = list(range(1, 9)) + [0x80]


v4l2_ctrl_type = enum
(
    V4L2_CTRL_TYPE_INTEGER,
    V4L2_CTRL_TYPE_BOOLEAN,
    V4L2_CTRL_TYPE_MENU,
    V4L2_CTRL_TYPE_BUTTON,
    V4L2_CTRL_TYPE_INTEGER64,
    V4L2_CTRL_TYPE_CTRL_CLASS,
    V4L2_CTRL_TYPE_STRING,
) = range(1, 8)


v4l2_tuner_type = enum
(
    V4L2_TUNER_RADIO,
    V4L2_TUNER_ANALOG_TV,
    V4L2_TUNER_DIGITAL_TV,
) = range(1, 4)


v4l2_memory = enum
(
    V4L2_MEMORY_MMAP,
    V4L2_MEMORY_USERPTR,
    V4L2_MEMORY_OVERLAY,
) = range(1, 4)


v4l2_colorspace = enum
(
    V4L2_COLORSPACE_SMPTE170M,
    V4L2_COLORSPACE_SMPTE240M,
    V4L2_COLORSPACE_REC709,
    V4L2_COLORSPACE_BT878,
    V4L2_COLORSPACE_470_SYSTEM_M,
    V4L2_COLORSPACE_470_SYSTEM_BG,
    V4L2_COLORSPACE_JPEG,
    V4L2_COLORSPACE_SRGB,
) = range(1, 9)


v4l2_priority = enum
(
    V4L2_PRIORITY_UNSET,
    V4L2_PRIORITY_BACKGROUND,
    V4L2_PRIORITY_INTERACTIVE,
    V4L2_PRIORITY_RECORD,
    V4L2_PRIORITY_DEFAULT,
) = list(range(0, 4)) + [2]


class v4l2_rect(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_int32),
        ('top', ctypes.c_int32),
        ('width', ctypes.c_int32),
        ('height', ctypes.c_int32),
    ]


class v4l2_fract(ctypes.Structure):
    _fields_ = [
        ('numerator', ctypes.c_uint32),
        ('denominator', ctypes.c_uint32),
    ]


#
# Driver capabilities
#

class v4l2_capability(ctypes.Structure):
    _fields_ = [
        ('driver', ctypes.c_char * 16),
        ('card', ctypes.c_char * 32),
        ('bus_info', ctypes.c_char * 32),
        ('version', ctypes.c_uint32),
        ('capabilities', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4),
    ]


#
# Values for 'capabilities' field
#

V4L2_CAP_VIDEO_CAPTURE = 0x00000001
V4L2_CAP_VIDEO_OUTPUT = 0x00000002
V4L2_CAP_VIDEO_OVERLAY = 0x00000004
V4L2_CAP_VBI_CAPTURE = 0x00000010
V4L2_CAP_VBI_OUTPUT = 0x00000020
V4L2_CAP_SLICED_VBI_CAPTURE = 0x00000040
V4L2_CAP_SLICED_VBI_OUTPUT = 0x00000080
V4L2_CAP_RDS_CAPTURE = 0x00000100
V4L2_CAP_VIDEO_OUTPUT_OVERLAY = 0x00000200
V4L2_CAP_HW_FREQ_SEEK = 0x00000400
V4L2_CAP_RDS_OUTPUT = 0x00000800

V4L2_CAP_TUNER = 0x00010000
V4L2_CAP_AUDIO = 0x00020000
V4L2_CAP_RADIO = 0x00040000
V4L2_CAP_MODULATOR = 0x00080000

V4L2_CAP_READWRITE = 0x01000000
V4L2_CAP_ASYNCIO = 0x02000000
V4L2_CAP_STREAMING = 0x04000000


#
# Video image format
#

class v4l2_pix_format(ctypes.Structure):
    _fields_ = [
        ('width', ctypes.c_uint32),
        ('height', ctypes.c_uint32),
        ('pixelformat', ctypes.c_uint32),
        ('field', v4l2_field),
        ('bytesperline', ctypes.c_uint32),
        ('sizeimage', ctypes.c_uint32),
        ('colorspace', v4l2_colorspace),
        ('priv', ctypes.c_uint32),
    ]

# RGB formats
V4L2_PIX_FMT_RGB332 = v4l2_fourcc('R', 'G', 'B', '1')
V4L2_PIX_FMT_RGB444 = v4l2_fourcc('R', '4', '4', '4')
V4L2_PIX_FMT_RGB555 = v4l2_fourcc('R', 'G', 'B', 'O')
V4L2_PIX_FMT_RGB565 = v4l2_fourcc('R', 'G', 'B', 'P')
V4L2_PIX_FMT_RGB555X = v4l2_fourcc('R', 'G', 'B', 'Q')
V4L2_PIX_FMT_RGB565X = v4l2_fourcc('R', 'G', 'B', 'R')
V4L2_PIX_FMT_BGR24 = v4l2_fourcc('B', 'G', 'R', '3')
V4L2_PIX_FMT_RGB24 = v4l2_fourcc('R', 'G', 'B', '3')
V4L2_PIX_FMT_BGR32 = v4l2_fourcc('B', 'G', 'R', '4')
V4L2_PIX_FMT_RGB32 = v4l2_fourcc('R', 'G', 'B', '4')

# Grey formats
V4L2_PIX_FMT_GREY = v4l2_fourcc('G', 'R', 'E', 'Y')
V4L2_PIX_FMT_Y10 =  v4l2_fourcc('Y', '1', '0', ' ')
V4L2_PIX_FMT_Y16 = v4l2_fourcc('Y', '1', '6', ' ')

# Palette formats
V4L2_PIX_FMT_PAL8 = v4l2_fourcc('P', 'A', 'L', '8')

# Luminance+Chrominance formats
V4L2_PIX_FMT_YVU410 = v4l2_fourcc('Y', 'V', 'U', '9')
V4L2_PIX_FMT_YVU420 = v4l2_fourcc('Y', 'V', '1', '2')
V4L2_PIX_FMT_YUYV = v4l2_fourcc('Y', 'U', 'Y', 'V')
V4L2_PIX_FMT_YYUV = v4l2_fourcc('Y', 'Y', 'U', 'V')
V4L2_PIX_FMT_YVYU = v4l2_fourcc('Y', 'V', 'Y', 'U')
V4L2_PIX_FMT_UYVY = v4l2_fourcc('U', 'Y', 'V', 'Y')
V4L2_PIX_FMT_VYUY = v4l2_fourcc('V', 'Y', 'U', 'Y')
V4L2_PIX_FMT_YUV422P = v4l2_fourcc('4', '2', '2', 'P')
V4L2_PIX_FMT_YUV411P = v4l2_fourcc('4', '1', '1', 'P')
V4L2_PIX_FMT_Y41P = v4l2_fourcc('Y', '4', '1', 'P')
V4L2_PIX_FMT_YUV444 = v4l2_fourcc('Y', '4', '4', '4')
V4L2_PIX_FMT_YUV555 = v4l2_fourcc('Y', 'U', 'V', 'O')
V4L2_PIX_FMT_YUV565 = v4l2_fourcc('Y', 'U', 'V', 'P')
V4L2_PIX_FMT_YUV32 = v4l2_fourcc('Y', 'U', 'V', '4')
V4L2_PIX_FMT_YUV410 = v4l2_fourcc('Y', 'U', 'V', '9')
V4L2_PIX_FMT_YUV420 = v4l2_fourcc('Y', 'U', '1', '2')
V4L2_PIX_FMT_HI240 = v4l2_fourcc('H', 'I', '2', '4')
V4L2_PIX_FMT_HM12 = v4l2_fourcc('H', 'M', '1', '2')

# two planes -- one Y, one Cr + Cb interleaved
V4L2_PIX_FMT_NV12 = v4l2_fourcc('N', 'V', '1', '2')
V4L2_PIX_FMT_NV21 = v4l2_fourcc('N', 'V', '2', '1')
V4L2_PIX_FMT_NV16 = v4l2_fourcc('N', 'V', '1', '6')
V4L2_PIX_FMT_NV61 = v4l2_fourcc('N', 'V', '6', '1')

# Bayer formats - see http://www.siliconimaging.com/RGB%20Bayer.htm
V4L2_PIX_FMT_SBGGR8 = v4l2_fourcc('B', 'A', '8', '1')
V4L2_PIX_FMT_SGBRG8 = v4l2_fourcc('G', 'B', 'R', 'G')
V4L2_PIX_FMT_SGRBG8 = v4l2_fourcc('G', 'R', 'B', 'G')
V4L2_PIX_FMT_SRGGB8 = v4l2_fourcc('R', 'G', 'G', 'B')
V4L2_PIX_FMT_SBGGR10 = v4l2_fourcc('B', 'G', '1', '0')
V4L2_PIX_FMT_SGBRG10 = v4l2_fourcc('G', 'B', '1', '0')
V4L2_PIX_FMT_SGRBG10 = v4l2_fourcc('B', 'A', '1', '0')
V4L2_PIX_FMT_SRGGB10 = v4l2_fourcc('R', 'G', '1', '0')
V4L2_PIX_FMT_SGRBG10DPCM8 = v4l2_fourcc('B', 'D', '1', '0')
V4L2_PIX_FMT_SBGGR16 = v4l2_fourcc('B', 'Y', 'R', '2')

# compressed formats
V4L2_PIX_FMT_MJPEG = v4l2_fourcc('M', 'J', 'P', 'G')
V4L2_PIX_FMT_JPEG = v4l2_fourcc('J', 'P', 'E', 'G')
V4L2_PIX_FMT_DV = v4l2_fourcc('d', 'v', 's', 'd')
V4L2_PIX_FMT_MPEG = v4l2_fourcc('M', 'P', 'E', 'G')

# Vendor-specific formats
V4L2_PIX_FMT_CPIA1 = v4l2_fourcc('C', 'P', 'I', 'A')
V4L2_PIX_FMT_WNVA = v4l2_fourcc('W', 'N', 'V', 'A')
V4L2_PIX_FMT_SN9C10X = v4l2_fourcc('S', '9', '1', '0')
V4L2_PIX_FMT_SN9C20X_I420 = v4l2_fourcc('S', '9', '2', '0')
V4L2_PIX_FMT_PWC1 = v4l2_fourcc('P', 'W', 'C', '1')
V4L2_PIX_FMT_PWC2 = v4l2_fourcc('P', 'W', 'C', '2')
V4L2_PIX_FMT_ET61X251 = v4l2_fourcc('E', '6', '2', '5')
V4L2_PIX_FMT_SPCA501 = v4l2_fourcc('S', '5', '0', '1')
V4L2_PIX_FMT_SPCA505 = v4l2_fourcc('S', '5', '0', '5')
V4L2_PIX_FMT_SPCA508 = v4l2_fourcc('S', '5', '0', '8')
V4L2_PIX_FMT_SPCA561 = v4l2_fourcc('S', '5', '6', '1')
V4L2_PIX_FMT_PAC207 = v4l2_fourcc('P', '2', '0', '7')
V4L2_PIX_FMT_MR97310A = v4l2_fourcc('M', '3', '1', '0')
V4L2_PIX_FMT_SN9C2028 = v4l2_fourcc('S', 'O', 'N', 'X')
V4L2_PIX_FMT_SQ905C = v4l2_fourcc('9', '0', '5', 'C')
V4L2_PIX_FMT_PJPG = v4l2_fourcc('P', 'J', 'P', 'G')
V4L2_PIX_FMT_OV511 = v4l2_fourcc('O', '5', '1', '1')
V4L2_PIX_FMT_OV518 = v4l2_fourcc('O', '5', '1', '8')
V4L2_PIX_FMT_STV0680 = v4l2_fourcc('S', '6', '8', '0')


#
# Format enumeration
#

class v4l2_fmtdesc(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('type', ctypes.c_int),
        ('flags', ctypes.c_uint32),
        ('description', ctypes.c_char * 32),
        ('pixelformat', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4),
    ]

V4L2_FMT_FLAG_COMPRESSED = 0x0001
V4L2_FMT_FLAG_EMULATED = 0x0002


#
# Experimental frame size and frame rate enumeration
#

v4l2_frmsizetypes = enum
(
    V4L2_FRMSIZE_TYPE_DISCRETE,
    V4L2_FRMSIZE_TYPE_CONTINUOUS,
    V4L2_FRMSIZE_TYPE_STEPWISE,
) = range(1, 4)


class v4l2_frmsize_discrete(ctypes.Structure):
    _fields_ = [
        ('width', ctypes.c_uint32),
        ('height', ctypes.c_uint32),
    ]


class v4l2_frmsize_stepwise(ctypes.Structure):
    _fields_ = [
        ('min_width', ctypes.c_uint32),
        ('min_height', ctypes.c_uint32),
        ('step_width', ctypes.c_uint32),
        ('min_height', ctypes.c_uint32),
        ('max_height', ctypes.c_uint32),
        ('step_height', ctypes.c_uint32),
    ]


class v4l2_frmsizeenum(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('discrete', v4l2_frmsize_discrete),
            ('stepwise', v4l2_frmsize_stepwise),
        ]

    _fields_ = [
        ('index', ctypes.c_uint32),
        ('pixel_format', ctypes.c_uint32),
        ('type', ctypes.c_uint32),
        ('_u', _u),
        ('reserved', ctypes.c_uint32 * 2)
    ]

    _anonymous_ = ('_u',)


#
# Frame rate enumeration
#

v4l2_frmivaltypes = enum
(
    V4L2_FRMIVAL_TYPE_DISCRETE,
    V4L2_FRMIVAL_TYPE_CONTINUOUS,
    V4L2_FRMIVAL_TYPE_STEPWISE,
) = range(1, 4)


class v4l2_frmival_stepwise(ctypes.Structure):
    _fields_ = [
        ('min', v4l2_fract),
        ('max', v4l2_fract),
        ('step', v4l2_fract),
    ]


class v4l2_frmivalenum(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('discrete', v4l2_fract),
            ('stepwise', v4l2_frmival_stepwise),
        ]

    _fields_ = [
        ('index', ctypes.c_uint32),
        ('pixel_format', ctypes.c_uint32),
        ('width', ctypes.c_uint32),
        ('height', ctypes.c_uint32),
        ('type', ctypes.c_uint32),
        ('_u', _u),
        ('reserved', ctypes.c_uint32 * 2),
    ]

    _anonymous_ = ('_u',)


#
# Timecode
#

class v4l2_timecode(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('frames', ctypes.c_uint8),
        ('seconds', ctypes.c_uint8),
        ('minutes', ctypes.c_uint8),
        ('hours', ctypes.c_uint8),
        ('userbits', ctypes.c_uint8 * 4),
    ]


V4L2_TC_TYPE_24FPS = 1
V4L2_TC_TYPE_25FPS = 2
V4L2_TC_TYPE_30FPS = 3
V4L2_TC_TYPE_50FPS = 4
V4L2_TC_TYPE_60FPS = 5

V4L2_TC_FLAG_DROPFRAME = 0x0001
V4L2_TC_FLAG_COLORFRAME = 0x0002
V4L2_TC_USERBITS_field = 0x000C
V4L2_TC_USERBITS_USERDEFINED = 0x0000
V4L2_TC_USERBITS_8BITCHARS = 0x0008


class v4l2_jpegcompression(ctypes.Structure):
    _fields_ = [
        ('quality', ctypes.c_int),
        ('APPn', ctypes.c_int),
        ('APP_len', ctypes.c_int),
        ('APP_data', ctypes.c_char * 60),
        ('COM_len', ctypes.c_int),
        ('COM_data', ctypes.c_char * 60),
        ('jpeg_markers', ctypes.c_uint32),
    ]


V4L2_JPEG_MARKER_DHT = 1 << 3
V4L2_JPEG_MARKER_DQT = 1 << 4
V4L2_JPEG_MARKER_DRI = 1 << 5
V4L2_JPEG_MARKER_COM = 1 << 6
V4L2_JPEG_MARKER_APP = 1 << 7


#
# Memory-mapping buffers
#

class v4l2_requestbuffers(ctypes.Structure):
    _fields_ = [
        ('count', ctypes.c_uint32),
        ('type', v4l2_buf_type),
        ('memory', v4l2_memory),
        ('reserved', ctypes.c_uint32 * 2),
    ]


class v4l2_buffer(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('offset', ctypes.c_uint32),
            ('userptr', ctypes.c_ulong),
        ]

    _fields_ = [
        ('index', ctypes.c_uint32),
        ('type', v4l2_buf_type),
        ('bytesused', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('field', v4l2_field),
        ('timestamp', timeval),
        ('timecode', v4l2_timecode),
        ('sequence', ctypes.c_uint32),
        ('memory', v4l2_memory),
        ('m', _u),
        ('length', ctypes.c_uint32),
        ('input', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32),
    ]


V4L2_BUF_FLAG_MAPPED = 0x0001
V4L2_BUF_FLAG_QUEUED = 0x0002
V4L2_BUF_FLAG_DONE = 0x0004
V4L2_BUF_FLAG_KEYFRAME = 0x0008
V4L2_BUF_FLAG_PFRAME = 0x0010
V4L2_BUF_FLAG_BFRAME = 0x0020
V4L2_BUF_FLAG_TIMECODE = 0x0100
V4L2_BUF_FLAG_INPUT = 0x0200


#
# Overlay preview
#

class v4l2_framebuffer(ctypes.Structure):
    _fields_ = [
        ('capability', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('base', ctypes.c_void_p),
        ('fmt', v4l2_pix_format),
    ]

V4L2_FBUF_CAP_EXTERNOVERLAY = 0x0001
V4L2_FBUF_CAP_CHROMAKEY	= 0x0002
V4L2_FBUF_CAP_LIST_CLIPPING = 0x0004
V4L2_FBUF_CAP_BITMAP_CLIPPING = 0x0008
V4L2_FBUF_CAP_LOCAL_ALPHA = 0x0010
V4L2_FBUF_CAP_GLOBAL_ALPHA = 0x0020
V4L2_FBUF_CAP_LOCAL_INV_ALPHA = 0x0040
V4L2_FBUF_CAP_SRC_CHROMAKEY = 0x0080

V4L2_FBUF_FLAG_PRIMARY = 0x0001
V4L2_FBUF_FLAG_OVERLAY = 0x0002
V4L2_FBUF_FLAG_CHROMAKEY = 0x0004
V4L2_FBUF_FLAG_LOCAL_ALPHA = 0x0008
V4L2_FBUF_FLAG_GLOBAL_ALPHA = 0x0010
V4L2_FBUF_FLAG_LOCAL_INV_ALPHA = 0x0020
V4L2_FBUF_FLAG_SRC_CHROMAKEY = 0x0040


class v4l2_clip(ctypes.Structure):
    pass
v4l2_clip._fields_ = [
    ('c', v4l2_rect),
    ('next', ctypes.POINTER(v4l2_clip)),
]


class v4l2_window(ctypes.Structure):
    _fields_ = [
        ('w', v4l2_rect),
        ('field', v4l2_field),
        ('chromakey', ctypes.c_uint32),
        ('clips', ctypes.POINTER(v4l2_clip)),
        ('clipcount', ctypes.c_uint32),
        ('bitmap', ctypes.c_void_p),
        ('global_alpha', ctypes.c_uint8),
    ]


#
# Capture parameters
#

class v4l2_captureparm(ctypes.Structure):
    _fields_ = [
        ('capability', ctypes.c_uint32),
        ('capturemode', ctypes.c_uint32),
        ('timeperframe', v4l2_fract),
        ('extendedmode', ctypes.c_uint32),
        ('readbuffers', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4),
    ]


V4L2_MODE_HIGHQUALITY = 0x0001
V4L2_CAP_TIMEPERFRAME = 0x1000


class v4l2_outputparm(ctypes.Structure):
    _fields_ = [
        ('capability', ctypes.c_uint32),
        ('outputmode', ctypes.c_uint32),
        ('timeperframe', v4l2_fract),
        ('extendedmode', ctypes.c_uint32),
        ('writebuffers', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4),
    ]


#
# Input image cropping
#

class v4l2_cropcap(ctypes.Structure):
    _fields_ = [
        ('type', v4l2_buf_type),
        ('bounds', v4l2_rect),
        ('defrect', v4l2_rect),
        ('pixelaspect', v4l2_fract),
    ]


class v4l2_crop(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_int),
        ('c', v4l2_rect),
    ]


#
# Analog video standard
#

v4l2_std_id = ctypes.c_uint64


V4L2_STD_PAL_B = 0x00000001
V4L2_STD_PAL_B1 = 0x00000002
V4L2_STD_PAL_G = 0x00000004
V4L2_STD_PAL_H = 0x00000008
V4L2_STD_PAL_I = 0x00000010
V4L2_STD_PAL_D = 0x00000020
V4L2_STD_PAL_D1 = 0x00000040
V4L2_STD_PAL_K = 0x00000080

V4L2_STD_PAL_M = 0x00000100
V4L2_STD_PAL_N = 0x00000200
V4L2_STD_PAL_Nc = 0x00000400
V4L2_STD_PAL_60 = 0x00000800

V4L2_STD_NTSC_M = 0x00001000
V4L2_STD_NTSC_M_JP = 0x00002000
V4L2_STD_NTSC_443 = 0x00004000
V4L2_STD_NTSC_M_KR = 0x00008000

V4L2_STD_SECAM_B = 0x00010000
V4L2_STD_SECAM_D = 0x00020000
V4L2_STD_SECAM_G = 0x00040000
V4L2_STD_SECAM_H = 0x00080000
V4L2_STD_SECAM_K = 0x00100000
V4L2_STD_SECAM_K1 = 0x00200000
V4L2_STD_SECAM_L = 0x00400000
V4L2_STD_SECAM_LC = 0x00800000

V4L2_STD_ATSC_8_VSB = 0x01000000
V4L2_STD_ATSC_16_VSB = 0x02000000


# some common needed stuff
V4L2_STD_PAL_BG = (V4L2_STD_PAL_B | V4L2_STD_PAL_B1 | V4L2_STD_PAL_G)
V4L2_STD_PAL_DK = (V4L2_STD_PAL_D | V4L2_STD_PAL_D1 | V4L2_STD_PAL_K)
V4L2_STD_PAL = (V4L2_STD_PAL_BG | V4L2_STD_PAL_DK | V4L2_STD_PAL_H | V4L2_STD_PAL_I)
V4L2_STD_NTSC = (V4L2_STD_NTSC_M | V4L2_STD_NTSC_M_JP | V4L2_STD_NTSC_M_KR)
V4L2_STD_SECAM_DK = (V4L2_STD_SECAM_D | V4L2_STD_SECAM_K | V4L2_STD_SECAM_K1)
V4L2_STD_SECAM = (V4L2_STD_SECAM_B | V4L2_STD_SECAM_G | V4L2_STD_SECAM_H | V4L2_STD_SECAM_DK | V4L2_STD_SECAM_L | V4L2_STD_SECAM_LC)

V4L2_STD_525_60 = (V4L2_STD_PAL_M | V4L2_STD_PAL_60 | V4L2_STD_NTSC | V4L2_STD_NTSC_443)
V4L2_STD_625_50 = (V4L2_STD_PAL | V4L2_STD_PAL_N | V4L2_STD_PAL_Nc | V4L2_STD_SECAM)
V4L2_STD_ATSC = (V4L2_STD_ATSC_8_VSB | V4L2_STD_ATSC_16_VSB)

V4L2_STD_UNKNOWN = 0
V4L2_STD_ALL = (V4L2_STD_525_60 | V4L2_STD_625_50)

# some merged standards
V4L2_STD_MN = (V4L2_STD_PAL_M | V4L2_STD_PAL_N | V4L2_STD_PAL_Nc | V4L2_STD_NTSC)
V4L2_STD_B = (V4L2_STD_PAL_B | V4L2_STD_PAL_B1 | V4L2_STD_SECAM_B)
V4L2_STD_GH = (V4L2_STD_PAL_G | V4L2_STD_PAL_H|V4L2_STD_SECAM_G | V4L2_STD_SECAM_H)
V4L2_STD_DK = (V4L2_STD_PAL_DK | V4L2_STD_SECAM_DK)


class v4l2_standard(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('id', v4l2_std_id),
        ('name', ctypes.c_char * 24),
        ('frameperiod', v4l2_fract),
        ('framelines', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4),
    ]


#
# Video timings dv preset
#

class v4l2_dv_preset(ctypes.Structure):
    _fields_ = [
        ('preset', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4)
    ]


#
# DV preset enumeration
#

class v4l2_dv_enum_preset(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('preset', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('width', ctypes.c_uint32),
        ('height', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4),
    ]

#
# DV preset values
#

V4L2_DV_INVALID = 0
V4L2_DV_480P59_94 = 1
V4L2_DV_576P50 = 2
V4L2_DV_720P24 = 3
V4L2_DV_720P25 = 4
V4L2_DV_720P30 = 5
V4L2_DV_720P50 = 6
V4L2_DV_720P59_94 = 7
V4L2_DV_720P60 = 8
V4L2_DV_1080I29_97 = 9
V4L2_DV_1080I30	= 10
V4L2_DV_1080I25	= 11
V4L2_DV_1080I50	= 12
V4L2_DV_1080I60	= 13
V4L2_DV_1080P24	= 14
V4L2_DV_1080P25	= 15
V4L2_DV_1080P30	= 16
V4L2_DV_1080P50	= 17
V4L2_DV_1080P60	= 18


#
# DV BT timings
#

class v4l2_bt_timings(ctypes.Structure):
    _fields_ = [
        ('width', ctypes.c_uint32),
        ('height', ctypes.c_uint32),
        ('interlaced', ctypes.c_uint32),
        ('polarities', ctypes.c_uint32),
        ('pixelclock', ctypes.c_uint64),
        ('hfrontporch', ctypes.c_uint32),
        ('hsync', ctypes.c_uint32),
        ('hbackporch', ctypes.c_uint32),
        ('vfrontporch', ctypes.c_uint32),
        ('vsync', ctypes.c_uint32),
        ('vbackporch', ctypes.c_uint32),
        ('il_vfrontporch', ctypes.c_uint32),
        ('il_vsync', ctypes.c_uint32),
        ('il_vbackporch', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 16),
    ]

    _pack_ = True

# Interlaced or progressive format
V4L2_DV_PROGRESSIVE = 0
V4L2_DV_INTERLACED = 1

# Polarities. If bit is not set, it is assumed to be negative polarity
V4L2_DV_VSYNC_POS_POL = 0x00000001
V4L2_DV_HSYNC_POS_POL = 0x00000002


class v4l2_dv_timings(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('bt', v4l2_bt_timings),
            ('reserved', ctypes.c_uint32 * 32),
        ]

    _fields_ = [
        ('type', ctypes.c_uint32),
        ('_u', _u),
    ]

    _anonymous_ = ('_u',)
    _pack_ = True


# Values for the type field
V4L2_DV_BT_656_1120 = 0


#
# Video inputs
#

class v4l2_input(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('type', ctypes.c_uint32),
        ('audioset', ctypes.c_uint32),
        ('tuner', ctypes.c_uint32),
        ('std', v4l2_std_id),
        ('status', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4),
    ]


V4L2_INPUT_TYPE_TUNER = 1
V4L2_INPUT_TYPE_CAMERA = 2

V4L2_IN_ST_NO_POWER = 0x00000001
V4L2_IN_ST_NO_SIGNAL = 0x00000002
V4L2_IN_ST_NO_COLOR = 0x00000004

V4L2_IN_ST_HFLIP = 0x00000010
V4L2_IN_ST_VFLIP = 0x00000020

V4L2_IN_ST_NO_H_LOCK = 0x00000100
V4L2_IN_ST_COLOR_KILL = 0x00000200

V4L2_IN_ST_NO_SYNC = 0x00010000
V4L2_IN_ST_NO_EQU = 0x00020000
V4L2_IN_ST_NO_CARRIER = 0x00040000

V4L2_IN_ST_MACROVISION = 0x01000000
V4L2_IN_ST_NO_ACCESS = 0x02000000
V4L2_IN_ST_VTR = 0x04000000

V4L2_IN_CAP_PRESETS = 0x00000001
V4L2_IN_CAP_CUSTOM_TIMINGS = 0x00000002
V4L2_IN_CAP_STD = 0x00000004

#
# Video outputs
#

class v4l2_output(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('type', ctypes.c_uint32),
        ('audioset', ctypes.c_uint32),
        ('modulator', ctypes.c_uint32),
        ('std', v4l2_std_id),
        ('reserved', ctypes.c_uint32 * 4),
    ]


V4L2_OUTPUT_TYPE_MODULATOR = 1
V4L2_OUTPUT_TYPE_ANALOG	= 2
V4L2_OUTPUT_TYPE_ANALOGVGAOVERLAY = 3

V4L2_OUT_CAP_PRESETS = 0x00000001
V4L2_OUT_CAP_CUSTOM_TIMINGS = 0x00000002
V4L2_OUT_CAP_STD = 0x00000004

#
# Controls
#

class v4l2_control(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_uint32),
        ('value', ctypes.c_int32),
    ]


class v4l2_ext_control(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('value', ctypes.c_int32),
            ('value64', ctypes.c_int64),
            ('reserved', ctypes.c_void_p),
        ]

    _fields_ = [
        ('id', ctypes.c_uint32),
        ('reserved2', ctypes.c_uint32 * 2),
        ('_u', _u)
    ]

    _anonymous_ = ('_u',)
    _pack_ = True


class v4l2_ext_controls(ctypes.Structure):
    _fields_ = [
        ('ctrl_class', ctypes.c_uint32),
        ('count', ctypes.c_uint32),
        ('error_idx', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 2),
        ('controls', ctypes.POINTER(v4l2_ext_control)),
    ]


V4L2_CTRL_CLASS_USER = 0x00980000
V4L2_CTRL_CLASS_MPEG = 0x00990000
V4L2_CTRL_CLASS_CAMERA = 0x009a0000
V4L2_CTRL_CLASS_FM_TX = 0x009b0000


def V4L2_CTRL_ID_MASK():
    return 0x0fffffff


def V4L2_CTRL_ID2CLASS(id_):
    return id_ & 0x0fff0000 # unsigned long


def V4L2_CTRL_DRIVER_PRIV(id_):
    return (id_ & 0xffff) >= 0x1000


class v4l2_queryctrl(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_uint32),
        ('type', v4l2_ctrl_type),
        ('name', ctypes.c_char * 32),
        ('minimum', ctypes.c_int32),
        ('maximum', ctypes.c_int32),
        ('step', ctypes.c_int32),
        ('default', ctypes.c_int32),
        ('flags', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 2),
    ]


class v4l2_querymenu(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_uint32),
        ('index', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('reserved', ctypes.c_uint32),
    ]


V4L2_CTRL_FLAG_DISABLED = 0x0001
V4L2_CTRL_FLAG_GRABBED = 0x0002
V4L2_CTRL_FLAG_READ_ONLY = 0x0004
V4L2_CTRL_FLAG_UPDATE = 0x0008
V4L2_CTRL_FLAG_INACTIVE = 0x0010
V4L2_CTRL_FLAG_SLIDER = 0x0020
V4L2_CTRL_FLAG_WRITE_ONLY = 0x0040

V4L2_CTRL_FLAG_NEXT_CTRL = 0x80000000

V4L2_CID_BASE = V4L2_CTRL_CLASS_USER | 0x900
V4L2_CID_USER_BASE = V4L2_CID_BASE
V4L2_CID_PRIVATE_BASE = 0x08000000

V4L2_CID_USER_CLASS = V4L2_CTRL_CLASS_USER | 1
V4L2_CID_BRIGHTNESS = V4L2_CID_BASE + 0
V4L2_CID_CONTRAST = V4L2_CID_BASE + 1
V4L2_CID_SATURATION = V4L2_CID_BASE + 2
V4L2_CID_HUE = V4L2_CID_BASE + 3
V4L2_CID_AUDIO_VOLUME = V4L2_CID_BASE + 5
V4L2_CID_AUDIO_BALANCE = V4L2_CID_BASE + 6
V4L2_CID_AUDIO_BASS = V4L2_CID_BASE + 7
V4L2_CID_AUDIO_TREBLE = V4L2_CID_BASE + 8
V4L2_CID_AUDIO_MUTE = V4L2_CID_BASE + 9
V4L2_CID_AUDIO_LOUDNESS = V4L2_CID_BASE + 10
V4L2_CID_BLACK_LEVEL = V4L2_CID_BASE + 11 # Deprecated
V4L2_CID_AUTO_WHITE_BALANCE = V4L2_CID_BASE + 12
V4L2_CID_DO_WHITE_BALANCE = V4L2_CID_BASE + 13
V4L2_CID_RED_BALANCE = V4L2_CID_BASE + 14
V4L2_CID_BLUE_BALANCE = V4L2_CID_BASE + 15
V4L2_CID_GAMMA = V4L2_CID_BASE + 16
V4L2_CID_WHITENESS = V4L2_CID_GAMMA # Deprecated
V4L2_CID_EXPOSURE = V4L2_CID_BASE + 17
V4L2_CID_AUTOGAIN = V4L2_CID_BASE + 18
V4L2_CID_GAIN = V4L2_CID_BASE + 19
V4L2_CID_HFLIP = V4L2_CID_BASE + 20
V4L2_CID_VFLIP = V4L2_CID_BASE + 21

# Deprecated; use V4L2_CID_PAN_RESET and V4L2_CID_TILT_RESET
V4L2_CID_HCENTER = V4L2_CID_BASE + 22
V4L2_CID_VCENTER = V4L2_CID_BASE + 23

V4L2_CID_POWER_LINE_FREQUENCY = V4L2_CID_BASE + 24

v4l2_power_line_frequency = enum
(
    V4L2_CID_POWER_LINE_FREQUENCY_DISABLED,
    V4L2_CID_POWER_LINE_FREQUENCY_50HZ,
    V4L2_CID_POWER_LINE_FREQUENCY_60HZ,
) = range(3)

V4L2_CID_HUE_AUTO = V4L2_CID_BASE + 25
V4L2_CID_WHITE_BALANCE_TEMPERATURE = V4L2_CID_BASE + 26
V4L2_CID_SHARPNESS = V4L2_CID_BASE + 27
V4L2_CID_BACKLIGHT_COMPENSATION = V4L2_CID_BASE + 28
V4L2_CID_CHROMA_AGC = V4L2_CID_BASE + 29
V4L2_CID_COLOR_KILLER = V4L2_CID_BASE + 30
V4L2_CID_COLORFX = V4L2_CID_BASE + 31

v4l2_colorfx = enum
(
    V4L2_COLORFX_NONE,
    V4L2_COLORFX_BW,
    V4L2_COLORFX_SEPIA,
) = range(3)

V4L2_CID_AUTOBRIGHTNESS = V4L2_CID_BASE + 32
V4L2_CID_BAND_STOP_FILTER = V4L2_CID_BASE + 33

V4L2_CID_ROTATE = V4L2_CID_BASE + 34
V4L2_CID_BG_COLOR = V4L2_CID_BASE + 35
V4L2_CID_LASTP1 = V4L2_CID_BASE + 36

V4L2_CID_MPEG_BASE = V4L2_CTRL_CLASS_MPEG | 0x900
V4L2_CID_MPEG_CLASS = V4L2_CTRL_CLASS_MPEG | 1

# MPEG streams
V4L2_CID_MPEG_STREAM_TYPE = V4L2_CID_MPEG_BASE + 0

v4l2_mpeg_stream_type = enum
(
    V4L2_MPEG_STREAM_TYPE_MPEG2_PS,
    V4L2_MPEG_STREAM_TYPE_MPEG2_TS,
    V4L2_MPEG_STREAM_TYPE_MPEG1_SS,
    V4L2_MPEG_STREAM_TYPE_MPEG2_DVD,
    V4L2_MPEG_STREAM_TYPE_MPEG1_VCD,
    V4L2_MPEG_STREAM_TYPE_MPEG2_SVCD,
) = range(6)

V4L2_CID_MPEG_STREAM_PID_PMT = V4L2_CID_MPEG_BASE + 1
V4L2_CID_MPEG_STREAM_PID_AUDIO = V4L2_CID_MPEG_BASE + 2
V4L2_CID_MPEG_STREAM_PID_VIDEO = V4L2_CID_MPEG_BASE + 3
V4L2_CID_MPEG_STREAM_PID_PCR = V4L2_CID_MPEG_BASE + 4
V4L2_CID_MPEG_STREAM_PES_ID_AUDIO = V4L2_CID_MPEG_BASE + 5
V4L2_CID_MPEG_STREAM_PES_ID_VIDEO = V4L2_CID_MPEG_BASE + 6
V4L2_CID_MPEG_STREAM_VBI_FMT = V4L2_CID_MPEG_BASE + 7

v4l2_mpeg_stream_vbi_fmt = enum
(
    V4L2_MPEG_STREAM_VBI_FMT_NONE,
    V4L2_MPEG_STREAM_VBI_FMT_IVTV,
) = range(2)

V4L2_CID_MPEG_AUDIO_SAMPLING_FREQ = V4L2_CID_MPEG_BASE + 100

v4l2_mpeg_audio_sampling_freq = enum
(
    V4L2_MPEG_AUDIO_SAMPLING_FREQ_44100,
    V4L2_MPEG_AUDIO_SAMPLING_FREQ_48000,
    V4L2_MPEG_AUDIO_SAMPLING_FREQ_32000,
) = range(3)

V4L2_CID_MPEG_AUDIO_ENCODING = V4L2_CID_MPEG_BASE + 101

v4l2_mpeg_audio_encoding = enum
(
    V4L2_MPEG_AUDIO_ENCODING_LAYER_1,
    V4L2_MPEG_AUDIO_ENCODING_LAYER_2,
    V4L2_MPEG_AUDIO_ENCODING_LAYER_3,
    V4L2_MPEG_AUDIO_ENCODING_AAC,
    V4L2_MPEG_AUDIO_ENCODING_AC3,
) = range(5)

V4L2_CID_MPEG_AUDIO_L1_BITRATE = V4L2_CID_MPEG_BASE + 102

v4l2_mpeg_audio_l1_bitrate = enum
(
    V4L2_MPEG_AUDIO_L1_BITRATE_32K,
    V4L2_MPEG_AUDIO_L1_BITRATE_64K,
    V4L2_MPEG_AUDIO_L1_BITRATE_96K,
    V4L2_MPEG_AUDIO_L1_BITRATE_128K,
    V4L2_MPEG_AUDIO_L1_BITRATE_160K,
    V4L2_MPEG_AUDIO_L1_BITRATE_192K,
    V4L2_MPEG_AUDIO_L1_BITRATE_224K,
    V4L2_MPEG_AUDIO_L1_BITRATE_256K,
    V4L2_MPEG_AUDIO_L1_BITRATE_288K,
    V4L2_MPEG_AUDIO_L1_BITRATE_320K,
    V4L2_MPEG_AUDIO_L1_BITRATE_352K,
    V4L2_MPEG_AUDIO_L1_BITRATE_384K,
    V4L2_MPEG_AUDIO_L1_BITRATE_416K,
    V4L2_MPEG_AUDIO_L1_BITRATE_448K,
) = range(14)

V4L2_CID_MPEG_AUDIO_L2_BITRATE = V4L2_CID_MPEG_BASE + 103

v4l2_mpeg_audio_l2_bitrate = enum
(
    V4L2_MPEG_AUDIO_L2_BITRATE_32K,
    V4L2_MPEG_AUDIO_L2_BITRATE_48K,
    V4L2_MPEG_AUDIO_L2_BITRATE_56K,
    V4L2_MPEG_AUDIO_L2_BITRATE_64K,
    V4L2_MPEG_AUDIO_L2_BITRATE_80K,
    V4L2_MPEG_AUDIO_L2_BITRATE_96K,
    V4L2_MPEG_AUDIO_L2_BITRATE_112K,
    V4L2_MPEG_AUDIO_L2_BITRATE_128K,
    V4L2_MPEG_AUDIO_L2_BITRATE_160K,
    V4L2_MPEG_AUDIO_L2_BITRATE_192K,
    V4L2_MPEG_AUDIO_L2_BITRATE_224K,
    V4L2_MPEG_AUDIO_L2_BITRATE_256K,
    V4L2_MPEG_AUDIO_L2_BITRATE_320K,
    V4L2_MPEG_AUDIO_L2_BITRATE_384K,
) = range(14)

V4L2_CID_MPEG_AUDIO_L3_BITRATE = V4L2_CID_MPEG_BASE + 104

v4l2_mpeg_audio_l3_bitrate = enum
(
    V4L2_MPEG_AUDIO_L3_BITRATE_32K,
    V4L2_MPEG_AUDIO_L3_BITRATE_40K,
    V4L2_MPEG_AUDIO_L3_BITRATE_48K,
    V4L2_MPEG_AUDIO_L3_BITRATE_56K,
    V4L2_MPEG_AUDIO_L3_BITRATE_64K,
    V4L2_MPEG_AUDIO_L3_BITRATE_80K,
    V4L2_MPEG_AUDIO_L3_BITRATE_96K,
    V4L2_MPEG_AUDIO_L3_BITRATE_112K,
    V4L2_MPEG_AUDIO_L3_BITRATE_128K,
    V4L2_MPEG_AUDIO_L3_BITRATE_160K,
    V4L2_MPEG_AUDIO_L3_BITRATE_192K,
    V4L2_MPEG_AUDIO_L3_BITRATE_224K,
    V4L2_MPEG_AUDIO_L3_BITRATE_256K,
    V4L2_MPEG_AUDIO_L3_BITRATE_320K,
) = range(14)

V4L2_CID_MPEG_AUDIO_MODE = V4L2_CID_MPEG_BASE + 105

v4l2_mpeg_audio_mode = enum
(
    V4L2_MPEG_AUDIO_MODE_STEREO,
    V4L2_MPEG_AUDIO_MODE_JOINT_STEREO,
    V4L2_MPEG_AUDIO_MODE_DUAL,
    V4L2_MPEG_AUDIO_MODE_MONO,
) = range(4)

V4L2_CID_MPEG_AUDIO_MODE_EXTENSION = V4L2_CID_MPEG_BASE + 106

v4l2_mpeg_audio_mode_extension = enum
(
    V4L2_MPEG_AUDIO_MODE_EXTENSION_BOUND_4,
    V4L2_MPEG_AUDIO_MODE_EXTENSION_BOUND_8,
    V4L2_MPEG_AUDIO_MODE_EXTENSION_BOUND_12,
    V4L2_MPEG_AUDIO_MODE_EXTENSION_BOUND_16,
) = range(4)

V4L2_CID_MPEG_AUDIO_EMPHASIS = V4L2_CID_MPEG_BASE + 107

v4l2_mpeg_audio_emphasis = enum
(
    V4L2_MPEG_AUDIO_EMPHASIS_NONE,
    V4L2_MPEG_AUDIO_EMPHASIS_50_DIV_15_uS,
    V4L2_MPEG_AUDIO_EMPHASIS_CCITT_J17,
) = range(3)

V4L2_CID_MPEG_AUDIO_CRC = V4L2_CID_MPEG_BASE + 108

v4l2_mpeg_audio_crc = enum
(
    V4L2_MPEG_AUDIO_CRC_NONE,
    V4L2_MPEG_AUDIO_CRC_CRC16,
) = range(2)

V4L2_CID_MPEG_AUDIO_MUTE = V4L2_CID_MPEG_BASE + 109
V4L2_CID_MPEG_AUDIO_AAC_BITRATE = V4L2_CID_MPEG_BASE + 110
V4L2_CID_MPEG_AUDIO_AC3_BITRATE	= V4L2_CID_MPEG_BASE + 111

v4l2_mpeg_audio_ac3_bitrate = enum
(
    V4L2_MPEG_AUDIO_AC3_BITRATE_32K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_40K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_48K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_56K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_64K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_80K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_96K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_112K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_128K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_160K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_192K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_224K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_256K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_320K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_384K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_448K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_512K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_576K,
    V4L2_MPEG_AUDIO_AC3_BITRATE_640K,
) = range(19)

V4L2_CID_MPEG_VIDEO_ENCODING = V4L2_CID_MPEG_BASE + 200

v4l2_mpeg_video_encoding = enum
(
    V4L2_MPEG_VIDEO_ENCODING_MPEG_1,
    V4L2_MPEG_VIDEO_ENCODING_MPEG_2,
    V4L2_MPEG_VIDEO_ENCODING_MPEG_4_AVC,
) = range(3)

V4L2_CID_MPEG_VIDEO_ASPECT = V4L2_CID_MPEG_BASE + 201

v4l2_mpeg_video_aspect = enum
(
    V4L2_MPEG_VIDEO_ASPECT_1x1,
    V4L2_MPEG_VIDEO_ASPECT_4x3,
    V4L2_MPEG_VIDEO_ASPECT_16x9,
    V4L2_MPEG_VIDEO_ASPECT_221x100,
) = range(4)

V4L2_CID_MPEG_VIDEO_B_FRAMES = V4L2_CID_MPEG_BASE + 202
V4L2_CID_MPEG_VIDEO_GOP_SIZE = V4L2_CID_MPEG_BASE + 203
V4L2_CID_MPEG_VIDEO_GOP_CLOSURE = V4L2_CID_MPEG_BASE + 204
V4L2_CID_MPEG_VIDEO_PULLDOWN = V4L2_CID_MPEG_BASE + 205
V4L2_CID_MPEG_VIDEO_BITRATE_MODE = V4L2_CID_MPEG_BASE + 206

v4l2_mpeg_video_bitrate_mode = enum
(
    V4L2_MPEG_VIDEO_BITRATE_MODE_VBR,
    V4L2_MPEG_VIDEO_BITRATE_MODE_CBR,
) = range(2)

V4L2_CID_MPEG_VIDEO_BITRATE = V4L2_CID_MPEG_BASE + 207
V4L2_CID_MPEG_VIDEO_BITRATE_PEAK = V4L2_CID_MPEG_BASE + 208
V4L2_CID_MPEG_VIDEO_TEMPORAL_DECIMATION = V4L2_CID_MPEG_BASE + 209
V4L2_CID_MPEG_VIDEO_MUTE = V4L2_CID_MPEG_BASE + 210
V4L2_CID_MPEG_VIDEO_MUTE_YUV = V4L2_CID_MPEG_BASE + 211

V4L2_CID_MPEG_CX2341X_BASE = V4L2_CTRL_CLASS_MPEG | 0x1000
V4L2_CID_MPEG_CX2341X_VIDEO_SPATIAL_FILTER_MODE = V4L2_CID_MPEG_CX2341X_BASE + 0

v4l2_mpeg_cx2341x_video_spatial_filter_mode = enum
(
    V4L2_MPEG_CX2341X_VIDEO_SPATIAL_FILTER_MODE_MANUAL,
    V4L2_MPEG_CX2341X_VIDEO_SPATIAL_FILTER_MODE_AUTO,
) = range(2)

V4L2_CID_MPEG_CX2341X_VIDEO_SPATIAL_FILTER = V4L2_CID_MPEG_CX2341X_BASE + 1
V4L2_CID_MPEG_CX2341X_VIDEO_LUMA_SPATIAL_FILTER_TYPE = V4L2_CID_MPEG_CX2341X_BASE + 2

v4l2_mpeg_cx2341x_video_luma_spatial_filter_type = enum
(
    V4L2_MPEG_CX2341X_VIDEO_LUMA_SPATIAL_FILTER_TYPE_OFF, 
    V4L2_MPEG_CX2341X_VIDEO_LUMA_SPATIAL_FILTER_TYPE_1D_HOR,
    V4L2_MPEG_CX2341X_VIDEO_LUMA_SPATIAL_FILTER_TYPE_1D_VERT,
    V4L2_MPEG_CX2341X_VIDEO_LUMA_SPATIAL_FILTER_TYPE_2D_HV_SEPARABLE,
    V4L2_MPEG_CX2341X_VIDEO_LUMA_SPATIAL_FILTER_TYPE_2D_SYM_NON_SEPARABLE,
) = range(5)

V4L2_CID_MPEG_CX2341X_VIDEO_CHROMA_SPATIAL_FILTER_TYPE = V4L2_CID_MPEG_CX2341X_BASE + 3

v4l2_mpeg_cx2341x_video_chroma_spatial_filter_type = enum
(
    V4L2_MPEG_CX2341X_VIDEO_CHROMA_SPATIAL_FILTER_TYPE_OFF,
    V4L2_MPEG_CX2341X_VIDEO_CHROMA_SPATIAL_FILTER_TYPE_1D_HOR,
) = range(2)

V4L2_CID_MPEG_CX2341X_VIDEO_TEMPORAL_FILTER_MODE = V4L2_CID_MPEG_CX2341X_BASE + 4

v4l2_mpeg_cx2341x_video_temporal_filter_mode = enum
(
    V4L2_MPEG_CX2341X_VIDEO_TEMPORAL_FILTER_MODE_MANUAL,
    V4L2_MPEG_CX2341X_VIDEO_TEMPORAL_FILTER_MODE_AUTO,
) = range(2)

V4L2_CID_MPEG_CX2341X_VIDEO_TEMPORAL_FILTER = V4L2_CID_MPEG_CX2341X_BASE + 5
V4L2_CID_MPEG_CX2341X_VIDEO_MEDIAN_FILTER_TYPE = V4L2_CID_MPEG_CX2341X_BASE + 6

v4l2_mpeg_cx2341x_video_median_filter_type = enum
(
    V4L2_MPEG_CX2341X_VIDEO_MEDIAN_FILTER_TYPE_OFF,
    V4L2_MPEG_CX2341X_VIDEO_MEDIAN_FILTER_TYPE_HOR,
    V4L2_MPEG_CX2341X_VIDEO_MEDIAN_FILTER_TYPE_VERT,
    V4L2_MPEG_CX2341X_VIDEO_MEDIAN_FILTER_TYPE_HOR_VERT,
    V4L2_MPEG_CX2341X_VIDEO_MEDIAN_FILTER_TYPE_DIAG,
) = range(5)

V4L2_CID_MPEG_CX2341X_VIDEO_LUMA_MEDIAN_FILTER_BOTTOM = V4L2_CID_MPEG_CX2341X_BASE + 7
V4L2_CID_MPEG_CX2341X_VIDEO_LUMA_MEDIAN_FILTER_TOP = V4L2_CID_MPEG_CX2341X_BASE + 8
V4L2_CID_MPEG_CX2341X_VIDEO_CHROMA_MEDIAN_FILTER_BOTTOM = V4L2_CID_MPEG_CX2341X_BASE + 9
V4L2_CID_MPEG_CX2341X_VIDEO_CHROMA_MEDIAN_FILTER_TOP = V4L2_CID_MPEG_CX2341X_BASE + 10
V4L2_CID_MPEG_CX2341X_STREAM_INSERT_NAV_PACKETS = V4L2_CID_MPEG_CX2341X_BASE + 11

V4L2_CID_CAMERA_CLASS_BASE = V4L2_CTRL_CLASS_CAMERA | 0x900
V4L2_CID_CAMERA_CLASS = V4L2_CTRL_CLASS_CAMERA | 1

V4L2_CID_EXPOSURE_AUTO = V4L2_CID_CAMERA_CLASS_BASE + 1

v4l2_exposure_auto_type = enum
(
    V4L2_EXPOSURE_AUTO,
    V4L2_EXPOSURE_MANUAL,
    V4L2_EXPOSURE_SHUTTER_PRIORITY,
    V4L2_EXPOSURE_APERTURE_PRIORITY,
) = range(4)

V4L2_CID_EXPOSURE_ABSOLUTE = V4L2_CID_CAMERA_CLASS_BASE + 2
V4L2_CID_EXPOSURE_AUTO_PRIORITY = V4L2_CID_CAMERA_CLASS_BASE + 3

V4L2_CID_PAN_RELATIVE = V4L2_CID_CAMERA_CLASS_BASE + 4
V4L2_CID_TILT_RELATIVE = V4L2_CID_CAMERA_CLASS_BASE + 5
V4L2_CID_PAN_RESET = V4L2_CID_CAMERA_CLASS_BASE + 6
V4L2_CID_TILT_RESET = V4L2_CID_CAMERA_CLASS_BASE + 7

V4L2_CID_PAN_ABSOLUTE = V4L2_CID_CAMERA_CLASS_BASE + 8
V4L2_CID_TILT_ABSOLUTE = V4L2_CID_CAMERA_CLASS_BASE + 9

V4L2_CID_FOCUS_ABSOLUTE = V4L2_CID_CAMERA_CLASS_BASE + 10
V4L2_CID_FOCUS_RELATIVE = V4L2_CID_CAMERA_CLASS_BASE + 11
V4L2_CID_FOCUS_AUTO = V4L2_CID_CAMERA_CLASS_BASE + 12

V4L2_CID_ZOOM_ABSOLUTE = V4L2_CID_CAMERA_CLASS_BASE + 13
V4L2_CID_ZOOM_RELATIVE = V4L2_CID_CAMERA_CLASS_BASE + 14
V4L2_CID_ZOOM_CONTINUOUS = V4L2_CID_CAMERA_CLASS_BASE + 15

V4L2_CID_PRIVACY = V4L2_CID_CAMERA_CLASS_BASE + 16

V4L2_CID_FM_TX_CLASS_BASE = V4L2_CTRL_CLASS_FM_TX | 0x900
V4L2_CID_FM_TX_CLASS = V4L2_CTRL_CLASS_FM_TX | 1

V4L2_CID_RDS_TX_DEVIATION = V4L2_CID_FM_TX_CLASS_BASE + 1
V4L2_CID_RDS_TX_PI = V4L2_CID_FM_TX_CLASS_BASE + 2
V4L2_CID_RDS_TX_PTY = V4L2_CID_FM_TX_CLASS_BASE + 3
V4L2_CID_RDS_TX_PS_NAME = V4L2_CID_FM_TX_CLASS_BASE + 5
V4L2_CID_RDS_TX_RADIO_TEXT = V4L2_CID_FM_TX_CLASS_BASE + 6

V4L2_CID_AUDIO_LIMITER_ENABLED = V4L2_CID_FM_TX_CLASS_BASE + 64
V4L2_CID_AUDIO_LIMITER_RELEASE_TIME = V4L2_CID_FM_TX_CLASS_BASE + 65
V4L2_CID_AUDIO_LIMITER_DEVIATION = V4L2_CID_FM_TX_CLASS_BASE + 66

V4L2_CID_AUDIO_COMPRESSION_ENABLED = V4L2_CID_FM_TX_CLASS_BASE + 80
V4L2_CID_AUDIO_COMPRESSION_GAIN = V4L2_CID_FM_TX_CLASS_BASE + 81
V4L2_CID_AUDIO_COMPRESSION_THRESHOLD = V4L2_CID_FM_TX_CLASS_BASE + 82
V4L2_CID_AUDIO_COMPRESSION_ATTACK_TIME = V4L2_CID_FM_TX_CLASS_BASE + 83
V4L2_CID_AUDIO_COMPRESSION_RELEASE_TIME = V4L2_CID_FM_TX_CLASS_BASE + 84

V4L2_CID_PILOT_TONE_ENABLED = V4L2_CID_FM_TX_CLASS_BASE + 96
V4L2_CID_PILOT_TONE_DEVIATION = V4L2_CID_FM_TX_CLASS_BASE + 97
V4L2_CID_PILOT_TONE_FREQUENCY = V4L2_CID_FM_TX_CLASS_BASE + 98

V4L2_CID_TUNE_PREEMPHASIS = V4L2_CID_FM_TX_CLASS_BASE + 112

v4l2_preemphasis = enum
(
    V4L2_PREEMPHASIS_DISABLED,
    V4L2_PREEMPHASIS_50_uS,
    V4L2_PREEMPHASIS_75_uS,
) = range(3)

V4L2_CID_TUNE_POWER_LEVEL = V4L2_CID_FM_TX_CLASS_BASE + 113
V4L2_CID_TUNE_ANTENNA_CAPACITOR = V4L2_CID_FM_TX_CLASS_BASE + 114


#
# Tuning
#

class v4l2_tuner(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('type', v4l2_tuner_type),
        ('capability', ctypes.c_uint32),
        ('rangelow', ctypes.c_uint32),
        ('rangehigh', ctypes.c_uint32),
        ('rxsubchans', ctypes.c_uint32),
        ('audmode', ctypes.c_uint32),
        ('signal', ctypes.c_int32),
        ('afc', ctypes.c_int32),
        ('reserved', ctypes.c_uint32 * 4),
    ]


class v4l2_modulator(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('capability', ctypes.c_uint32),
        ('rangelow', ctypes.c_uint32),
        ('rangehigh', ctypes.c_uint32),
        ('txsubchans', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4),
    ]


V4L2_TUNER_CAP_LOW = 0x0001
V4L2_TUNER_CAP_NORM = 0x0002
V4L2_TUNER_CAP_STEREO = 0x0010
V4L2_TUNER_CAP_LANG2 = 0x0020
V4L2_TUNER_CAP_SAP = 0x0020
V4L2_TUNER_CAP_LANG1 = 0x0040
V4L2_TUNER_CAP_RDS = 0x0080

V4L2_TUNER_SUB_MONO = 0x0001
V4L2_TUNER_SUB_STEREO = 0x0002
V4L2_TUNER_SUB_LANG2 = 0x0004
V4L2_TUNER_SUB_SAP = 0x0004
V4L2_TUNER_SUB_LANG1 = 0x0008
V4L2_TUNER_SUB_RDS = 0x0010

V4L2_TUNER_MODE_MONO = 0x0000
V4L2_TUNER_MODE_STEREO = 0x0001
V4L2_TUNER_MODE_LANG2 = 0x0002
V4L2_TUNER_MODE_SAP = 0x0002
V4L2_TUNER_MODE_LANG1 = 0x0003
V4L2_TUNER_MODE_LANG1_LANG2 = 0x0004


class v4l2_frequency(ctypes.Structure):
    _fields_ = [
        ('tuner', ctypes.c_uint32),
        ('type', v4l2_tuner_type),
        ('frequency', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 8),
    ]


class v4l2_hw_freq_seek(ctypes.Structure):
    _fields_ = [
        ('tuner', ctypes.c_uint32),
        ('type', v4l2_tuner_type),
        ('seek_upward', ctypes.c_uint32),
        ('wrap_around', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 8),
    ]


#
# RDS
#

class v4l2_rds_data(ctypes.Structure):
    _fields_ = [
        ('lsb', ctypes.c_char),
        ('msb', ctypes.c_char),
        ('block', ctypes.c_char),
    ]

    _pack_ = True


V4L2_RDS_BLOCK_MSK =  0x7
V4L2_RDS_BLOCK_A = 0
V4L2_RDS_BLOCK_B = 1
V4L2_RDS_BLOCK_C = 2
V4L2_RDS_BLOCK_D = 3
V4L2_RDS_BLOCK_C_ALT = 4
V4L2_RDS_BLOCK_INVALID = 7

V4L2_RDS_BLOCK_CORRECTED = 0x40
V4L2_RDS_BLOCK_ERROR = 0x80


#
# Audio
#

class v4l2_audio(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('capability', ctypes.c_uint32),
        ('mode', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 2),
    ]


V4L2_AUDCAP_STEREO = 0x00001
V4L2_AUDCAP_AVL = 0x00002

V4L2_AUDMODE_AVL = 0x00001


class v4l2_audioout(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('capability', ctypes.c_uint32),
        ('mode', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 2),
    ]


#
# Mpeg services (experimental)
#

V4L2_ENC_IDX_FRAME_I = 0
V4L2_ENC_IDX_FRAME_P = 1
V4L2_ENC_IDX_FRAME_B = 2
V4L2_ENC_IDX_FRAME_MASK = 0xf


class v4l2_enc_idx_entry(ctypes.Structure):
    _fields_ = [
        ('offset', ctypes.c_uint64),
        ('pts', ctypes.c_uint64),
        ('length', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 2),
    ]


V4L2_ENC_IDX_ENTRIES = 64


class v4l2_enc_idx(ctypes.Structure):
    _fields_ = [
        ('entries', ctypes.c_uint32),
        ('entries_cap', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 4),
        ('entry', v4l2_enc_idx_entry * V4L2_ENC_IDX_ENTRIES),
    ]


V4L2_ENC_CMD_START = 0
V4L2_ENC_CMD_STOP = 1
V4L2_ENC_CMD_PAUSE = 2
V4L2_ENC_CMD_RESUME = 3

V4L2_ENC_CMD_STOP_AT_GOP_END = 1 << 0


class v4l2_encoder_cmd(ctypes.Structure):
    class _u(ctypes.Union):
        class _s(ctypes.Structure):
            _fields_ = [
                ('data', ctypes.c_uint32 * 8),
            ]

        _fields_ = [
            ('raw', _s),
        ]

    _fields_ = [
        ('cmd', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('_u', _u),
    ]

    _anonymous_ = ('_u',)


#
# Data services (VBI)
#

class v4l2_vbi_format(ctypes.Structure):
    _fields_ = [
        ('sampling_rate', ctypes.c_uint32),
        ('offset', ctypes.c_uint32),
        ('samples_per_line', ctypes.c_uint32),
        ('sample_format', ctypes.c_uint32),
        ('start', ctypes.c_int32 * 2),
        ('count', ctypes.c_uint32 * 2),
        ('flags', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 2),
    ]


V4L2_VBI_UNSYNC = 1 << 0
V4L2_VBI_INTERLACED = 1 << 1


class v4l2_sliced_vbi_format(ctypes.Structure):
    _fields_ = [
        ('service_set', ctypes.c_uint16),
        ('service_lines', ctypes.c_uint16 * 2 * 24),
        ('io_size', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 2),
    ]


V4L2_SLICED_TELETEXT_B = 0x0001
V4L2_SLICED_VPS = 0x0400
V4L2_SLICED_CAPTION_525 = 0x1000
V4L2_SLICED_WSS_625 = 0x4000
V4L2_SLICED_VBI_525 = V4L2_SLICED_CAPTION_525
V4L2_SLICED_VBI_625 = (
    V4L2_SLICED_TELETEXT_B | V4L2_SLICED_VPS | V4L2_SLICED_WSS_625)


class v4l2_sliced_vbi_cap(ctypes.Structure):
    _fields_ = [
        ('service_set', ctypes.c_uint16),
        ('service_lines', ctypes.c_uint16 * 2 * 24),
        ('type', v4l2_buf_type),
        ('reserved', ctypes.c_uint32 * 3),
    ]


class v4l2_sliced_vbi_data(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_uint32),
        ('field', ctypes.c_uint32),
        ('line', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32),
        ('data', ctypes.c_char * 48),
    ]


#
# Sliced VBI data inserted into MPEG Streams
#


V4L2_MPEG_VBI_IVTV_TELETEXT_B = 1
V4L2_MPEG_VBI_IVTV_CAPTION_525 = 4
V4L2_MPEG_VBI_IVTV_WSS_625 = 5
V4L2_MPEG_VBI_IVTV_VPS = 7


class v4l2_mpeg_vbi_itv0_line(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_char),
        ('data', ctypes.c_char * 42),
    ]

    _pack_ = True


class v4l2_mpeg_vbi_itv0(ctypes.Structure):
    _fields_ = [
        ('linemask', ctypes.c_uint32 * 2), # how to define __le32 in ctypes?
        ('line', v4l2_mpeg_vbi_itv0_line * 35),
    ]

    _pack_ = True


class v4l2_mpeg_vbi_ITV0(ctypes.Structure):
    _fields_ = [
        ('line', v4l2_mpeg_vbi_itv0_line * 36),
    ]

    _pack_ = True


V4L2_MPEG_VBI_IVTV_MAGIC0 = "itv0"
V4L2_MPEG_VBI_IVTV_MAGIC1 = "ITV0"


class v4l2_mpeg_vbi_fmt_ivtv(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('itv0', v4l2_mpeg_vbi_itv0),
            ('ITV0', v4l2_mpeg_vbi_ITV0),
        ]

    _fields_ = [
        ('magic', ctypes.c_char * 4),
        ('_u', _u)
    ]

    _anonymous_ = ('_u',)
    _pack_ = True


#
# Aggregate structures
#

class v4l2_format(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('pix', v4l2_pix_format),
            ('win', v4l2_window),
            ('vbi', v4l2_vbi_format),
            ('sliced', v4l2_sliced_vbi_format),
            ('raw_data', ctypes.c_char * 200),
        ]

    _fields_ = [
        ('type', v4l2_buf_type),
        ('fmt', _u),
    ]


class v4l2_streamparm(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('capture', v4l2_captureparm),
            ('output', v4l2_outputparm),
            ('raw_data', ctypes.c_char * 200),
        ]

    _fields_ = [
        ('type', v4l2_buf_type),
        ('parm', _u)
    ]


#
# Advanced debugging
#

V4L2_CHIP_MATCH_HOST = 0
V4L2_CHIP_MATCH_I2C_DRIVER = 1
V4L2_CHIP_MATCH_I2C_ADDR = 2
V4L2_CHIP_MATCH_AC97 = 3


class v4l2_dbg_match(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('addr', ctypes.c_uint32),
            ('name', ctypes.c_char * 32),
        ]

    _fields_ = [
        ('type', ctypes.c_uint32),
        ('_u', _u),
    ]

    _anonymous_ = ('_u',)
    _pack_ = True


class v4l2_dbg_register(ctypes.Structure):
    _fields_ = [
        ('match', v4l2_dbg_match),
        ('size', ctypes.c_uint32),
        ('reg', ctypes.c_uint64),
        ('val', ctypes.c_uint64),
    ]

    _pack_ = True


class v4l2_dbg_chip_ident(ctypes.Structure):
    _fields_ = [
        ('match', v4l2_dbg_match),
        ('ident', ctypes.c_uint32),
        ('revision', ctypes.c_uint32),
    ]

    _pack_ = True


#
# ioctl codes for video devices
#

VIDIOC_QUERYCAP = _IOR('V', 0, v4l2_capability)
VIDIOC_RESERVED = _IO('V', 1)
VIDIOC_ENUM_FMT = _IOWR('V', 2, v4l2_fmtdesc)
VIDIOC_G_FMT = _IOWR('V', 4, v4l2_format)
VIDIOC_S_FMT = _IOWR('V', 5, v4l2_format)
VIDIOC_REQBUFS = _IOWR('V', 8, v4l2_requestbuffers)
VIDIOC_QUERYBUF	= _IOWR('V', 9, v4l2_buffer)
VIDIOC_G_FBUF = _IOR('V', 10, v4l2_framebuffer)
VIDIOC_S_FBUF = _IOW('V', 11, v4l2_framebuffer)
VIDIOC_OVERLAY = _IOW('V', 14, ctypes.c_int)
VIDIOC_QBUF = _IOWR('V', 15, v4l2_buffer)
VIDIOC_DQBUF = _IOWR('V', 17, v4l2_buffer)
VIDIOC_STREAMON = _IOW('V', 18, ctypes.c_int)
VIDIOC_STREAMOFF = _IOW('V', 19, ctypes.c_int)
VIDIOC_G_PARM = _IOWR('V', 21, v4l2_streamparm)
VIDIOC_S_PARM = _IOWR('V', 22, v4l2_streamparm)
VIDIOC_G_STD = _IOR('V', 23, v4l2_std_id)
VIDIOC_S_STD = _IOW('V', 24, v4l2_std_id)
VIDIOC_ENUMSTD = _IOWR('V', 25, v4l2_standard)
VIDIOC_ENUMINPUT = _IOWR('V', 26, v4l2_input)
VIDIOC_G_CTRL = _IOWR('V', 27, v4l2_control)
VIDIOC_S_CTRL = _IOWR('V', 28, v4l2_control)
VIDIOC_G_TUNER = _IOWR('V', 29, v4l2_tuner)
VIDIOC_S_TUNER = _IOW('V', 30, v4l2_tuner)
VIDIOC_G_AUDIO = _IOR('V', 33, v4l2_audio)
VIDIOC_S_AUDIO = _IOW('V', 34, v4l2_audio)
VIDIOC_QUERYCTRL = _IOWR('V', 36, v4l2_queryctrl)
VIDIOC_QUERYMENU = _IOWR('V', 37, v4l2_querymenu)
VIDIOC_G_INPUT = _IOR('V', 38, ctypes.c_int)
VIDIOC_S_INPUT = _IOWR('V', 39, ctypes.c_int)
VIDIOC_G_OUTPUT = _IOR('V', 46, ctypes.c_int)
VIDIOC_S_OUTPUT = _IOWR('V', 47, ctypes.c_int)
VIDIOC_ENUMOUTPUT = _IOWR('V', 48, v4l2_output)
VIDIOC_G_AUDOUT = _IOR('V', 49, v4l2_audioout)
VIDIOC_S_AUDOUT	= _IOW('V', 50, v4l2_audioout)
VIDIOC_G_MODULATOR = _IOWR('V', 54, v4l2_modulator)
VIDIOC_S_MODULATOR = _IOW('V', 55, v4l2_modulator)
VIDIOC_G_FREQUENCY = _IOWR('V', 56, v4l2_frequency)
VIDIOC_S_FREQUENCY = _IOW('V', 57, v4l2_frequency)
VIDIOC_CROPCAP = _IOWR('V', 58, v4l2_cropcap)
VIDIOC_G_CROP = _IOWR('V', 59, v4l2_crop)
VIDIOC_S_CROP = _IOW('V', 60, v4l2_crop)
VIDIOC_G_JPEGCOMP = _IOR('V', 61, v4l2_jpegcompression)
VIDIOC_S_JPEGCOMP = _IOW('V', 62, v4l2_jpegcompression)
VIDIOC_QUERYSTD = _IOR('V', 63, v4l2_std_id)
VIDIOC_TRY_FMT = _IOWR('V', 64, v4l2_format)
VIDIOC_ENUMAUDIO = _IOWR('V', 65, v4l2_audio)
VIDIOC_ENUMAUDOUT = _IOWR('V', 66, v4l2_audioout)
VIDIOC_G_PRIORITY = _IOR('V', 67, v4l2_priority)
VIDIOC_S_PRIORITY = _IOW('V', 68, v4l2_priority)
VIDIOC_G_SLICED_VBI_CAP = _IOWR('V', 69, v4l2_sliced_vbi_cap)
VIDIOC_LOG_STATUS = _IO('V', 70)
VIDIOC_G_EXT_CTRLS = _IOWR('V', 71, v4l2_ext_controls)
VIDIOC_S_EXT_CTRLS = _IOWR('V', 72, v4l2_ext_controls)
VIDIOC_TRY_EXT_CTRLS = _IOWR('V', 73, v4l2_ext_controls)

VIDIOC_ENUM_FRAMESIZES = _IOWR('V', 74, v4l2_frmsizeenum)
VIDIOC_ENUM_FRAMEINTERVALS = _IOWR('V', 75, v4l2_frmivalenum)
VIDIOC_G_ENC_INDEX = _IOR('V', 76, v4l2_enc_idx)
VIDIOC_ENCODER_CMD = _IOWR('V', 77, v4l2_encoder_cmd)
VIDIOC_TRY_ENCODER_CMD = _IOWR('V', 78, v4l2_encoder_cmd)

VIDIOC_DBG_S_REGISTER = _IOW('V', 79, v4l2_dbg_register)
VIDIOC_DBG_G_REGISTER = _IOWR('V', 80, v4l2_dbg_register)

VIDIOC_DBG_G_CHIP_IDENT = _IOWR('V', 81, v4l2_dbg_chip_ident)

VIDIOC_S_HW_FREQ_SEEK = _IOW('V', 82, v4l2_hw_freq_seek)
VIDIOC_ENUM_DV_PRESETS = _IOWR('V', 83, v4l2_dv_enum_preset)
VIDIOC_S_DV_PRESET = _IOWR('V', 84, v4l2_dv_preset)
VIDIOC_G_DV_PRESET = _IOWR('V', 85, v4l2_dv_preset)
VIDIOC_QUERY_DV_PRESET = _IOR('V', 86, v4l2_dv_preset)
VIDIOC_S_DV_TIMINGS = _IOWR('V', 87, v4l2_dv_timings)
VIDIOC_G_DV_TIMINGS = _IOWR('V', 88, v4l2_dv_timings)

VIDIOC_OVERLAY_OLD = _IOWR('V', 14, ctypes.c_int)
VIDIOC_S_PARM_OLD = _IOW('V', 22, v4l2_streamparm)
VIDIOC_S_CTRL_OLD = _IOW('V', 28, v4l2_control)
VIDIOC_G_AUDIO_OLD = _IOWR('V', 33, v4l2_audio)
VIDIOC_G_AUDOUT_OLD = _IOWR('V', 49, v4l2_audioout)
VIDIOC_CROPCAP_OLD = _IOR('V', 58, v4l2_cropcap)

BASE_VIDIOC_PRIVATE = 192
