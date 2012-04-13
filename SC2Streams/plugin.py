###
# Copyright (c) 2012, SC2Streams
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


class SC2Streams(callbacks.Plugin):
    
        
    def streams(self, irc, msg, args, arg1, arg2):
        """
        !streams [race] [numstreams].
        !streams [z|p|t] [1-10].

        Lists the current live streams. Can be limited to a specific number of streams, or both.
        
        Example: !streams z 5                                            
        
    
        by P.O'Connor
        """

        def isRace(s):
            try:
                if s.lower() in 'ztp':
                    return True
            except ValueError:
                irc.error("You didnt enter a valid race")
                return False

        if ircutils.isChannel(msg.args[0]):
            ircChannel = msg.args[0].lower()
        else:
            irc.error("This command shouldn't be launched from a PM")
            return

        #default values
        maxWidth = 0
        numStreams = 3
        streamRace = '-'
        
        # check if arguments are not given
        if arg1 == None:
            arg1 = "None"
        if arg2 == None:
            arg2 = "None"
        # check arguments that are given
        if arg1.isdigit():
                numStreams = int(arg1)
                if int(numStreams) > 10:
                        irc.error("The number you entered is too large")
                        return
        elif isRace(arg1):
                streamRace = arg1.lower()
                if arg2.isdigit():
                        numStreams = int(arg2)
                        if numStreams > 10:
                                irc.error("The number you entered is too large")
                                return

        #Download File
        request = urllib2.Request('http://www.teamliquid.net/video/streams/?xml=1&filter=live')
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
            # only SC2 Streams
            if stream.get("type").lower() == "sc2":
                # get title
                for channel in stream.findall("channel"):
                    title = channel.get("title", "")
                    if len(title) > maxWidth:
                        maxWidth = len(title)
                # get url
                for link in stream.findall("link"):
                    if link.get("type") == "embed":
                        url = link.text
                # get viewers
                    viewers = stream.get("viewers","0")
                # get race
                race = stream.get("race","-").lower()

                # get color based on race
                if race == 'z':
                    color = "\0036"     # purple
                elif race == 't':
                    color = "\0034"     # red
                elif race == 'p':
                    color = "\0037"     # yellow
                else:
                    color = "\00314"    # brown

                # populate STREAMS list
                STREAMS.append([viewers, title, url, race, color])



        # Sort List by viewers
        sorted_streams = sorted(STREAMS, key=lambda x: int(x[0]), reverse=True)

        if isRace(streamRace):
            race_streams = ([x for x in sorted_streams if x[3] == streamRace])
            streams = ([x for x in race_streams if race_streams.index(x) < numStreams])
        else:
            streams = ([x for x in sorted_streams if sorted_streams.index(x) < numStreams])

        # output header
        header = '{format}  {0:8} {1:{maxWidth}} {2}\002'.format("Viewers",\
                    "Title", " Link", maxWidth=maxWidth,format="\002\0033")
        irc.sendMsg(ircmsgs.privmsg(ircChannel, header))
        # Output Streams
        for i in range(len(streams)):
            streamMsg = '{color}#{0:3}{viewers:6}\002{title:{maxWidth}}\002\00314{url}'\
                        .format(str(i+1), viewers=streams[i][0], title=streams[i][1],
                        url=streams[i][2], maxWidth=maxWidth+1, color=streams[i][4])
            irc.sendMsg(ircmsgs.privmsg(ircChannel, streamMsg))
    streams = wrap(streams, [optional('something'), optional('something')])

Class = SC2Streams        




# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
