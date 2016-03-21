FFmpeg static build
===================

Three scripts to make a static build of ffmpeg with all the latest codecs and non-free/non-redistributable.

Just follow the instructions below. Once you have the build dependencies,
just run ./build.py, wait and you should get the ffmpeg binary in target/bin

Build dependencies (WIP)
------------------

	# Redhat & Centos
	$ yum groupinstall "Development Tools"
	$ yum install git glibc-static libstdc++-static cmake 

    # Debian & Ubuntu
    $ apt-get install build-essential curl tar <FIXME???>

	# OS X
	# install XCode, it can be found at http://developer.apple.com/
	# (apple login needed)
	# <FIXME???>


Codecs
------
* dcadec
* fdk-aac (non-free)
* mp3lame
* openjpeg
* vorbis
* theora
* vpx
* speex
* x264
* x265
* soxr
* twolame
* wavpack
* nvenc (h264/hevc nVidia)
* blackmagic (Decklink I/O)
* openssl

Codecs TODO
-----------
* webp
* opus
* schrodeinger
* iLBC
* libmfx (Intel HW accel)
* OpenCORE AMR
* RTMPDump
* VisualOn AMR-WB
* z.lib (zimg)
* GSM
* FreeType
* Fontconfig
* Frei0r
* libass
* libxml2 (dependency)
* libblurray
* libbs2b
* kvazaar (HEVC)
* openh264
* vid.stab (video stabilization)


Debug
-----

On the top-level of the project, run:

	$ . env.source
	
You can then enter the source folders and make the compilation yourself

	$ cd build/ffmpeg-*
	$ ./configure --prefix=$TARGET_DIR #...
	# ...


TODO
----

 * update `env.source` with the values that match `1_build.py` 
 * add Python3 support
 * compile `git` to remove OS library dependency
 * compile `cmake` to remove OS library dependency
 * `nasm` support in `mp3lame` (compile ourselves?)
 * test on OS X
 * add support for more codecs and libraries

 
