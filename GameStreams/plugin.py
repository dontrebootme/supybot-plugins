###
# Copyright (c) 2012, GameStreams
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import urllib2, StringIO, gzip
from xml.etree import ElementTree as ET


class GameStreams(callbacks.Plugin):
    
        
    def streams(self, irc, msg, args, arg1, arg2):
        """
        !streams [numstreams].
        !streams [1-10].

        Lists the current live streams. Can be limited to a specific number of streams.
        
        Example: !streams 5                                            
        
    
        by P.O'Connor
        """

        if ircutils.isChannel(msg.args[0]):
            ircChannel = msg.args[0].lower()
        else:
            irc.error("This command shouldn't be launched from a PM")
            return

        #default values
        maxWidth = 0
        numStreams = 3
        
        # check if arguments are not given
        if arg1 == None:
            arg1 = "None"
        # check arguments that are given
        if arg1.isdigit():
                numStreams = int(arg1)
                if int(numStreams) > 10:
                        irc.error("The number you entered is too large")
                        return
        #Download File
        request = urllib2.Request('http://api.justin.tv/api/stream/list.xml?category=gaming&limit=10')
        opener = urllib2.build_opener()
        request.add_header('Accept-encoding', 'gzip')
        request.add_header('User-Agent', 'Python-urllib/2.7 \
             patrick@theoconnor.com https://github.com/Antibody/supybot-plugins')
        response = opener.open(request)
    
        #Decompress
        compresseddata = StringIO.StringIO(response.read())
        uncompresseddata = gzip.GzipFile(fileobj=compresseddata)

        #Parse Elements
        stream_list = ET.parse(uncompresseddata)
        #Build Lists
        STREAMS = []
        for stream in stream_list.findall("stream"):
                # get title
                for channel in stream.findall("channel"):
                    title = channel.get("status", "")
                    if len(title) > maxWidth:
                        maxWidth = len(title)
                # get url
                    url = link.get("channel_url",""):
                # get viewers
                for channel_count in stream.findall("channel_count"):
                    viewers = channel_count.get("channel_count","0")

                # populate STREAMS list
                STREAMS.append([viewers, title, url, race, color])



        # Sort List by viewers
        sorted_streams = sorted(STREAMS, key=lambda x: int(x[0]), reverse=True)

        streams = ([x for x in sorted_streams if sorted_streams.index(x) < numStreams])

        # output header
        header = '{format}  {0:8} {1:{maxWidth}} {2}\002'.format("Viewers",\
                    "Title", " Link", maxWidth=maxWidth,format="\002\0033")
        irc.sendMsg(ircmsgs.privmsg(ircChannel, header))
        # Output Streams
        for i in range(len(streams)):
            streamMsg = '#{0:3}{viewers:6}\002{title:{maxWidth}}\002\00314{url}'\
                        .format(str(i+1), viewers=streams[i][0], title=streams[i][1],
                        url=streams[i][2], maxWidth=maxWidth+1)
            irc.sendMsg(ircmsgs.privmsg(ircChannel, streamMsg))
    streams = wrap(streams, [optional('something'), optional('something')])

Class = GameStreams        

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
