import argparse
import asyncio
import json
import logging
import os
import platform
import ssl

from aiohttp import web

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

ROOT = os.path.dirname(__file__)

relay = None
webcam = None


def create_local_tracks():
    global relay, webcam

    options = {"framerate": "30", "video_size": "640x480"}
    if relay is None:
        if platform.system() == "Darwin":
            webcam = MediaPlayer(
                "default:none", format="avfoundation", options=options
            )
        elif platform.system() == "Windows":
            webcam = MediaPlayer(
                "video=Integrated Camera", format="dshow", options=options
            )
        else:
            webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
        relay = MediaRelay()
    return None, relay.subscribe(webcam.video)


async def index(request):
    content = open(os.path.join(ROOT, "../../index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "../../client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc1 = RTCPeerConnection()
    pcs.add(pc1)

    @pc1.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc1.connectionState)
        if pc1.connectionState == "failed":
            await pc1.close()
            pcs.discard(pc1)

    # open media source
    audio, video = create_local_tracks()

    await pc1.setRemoteDescription(offer)
    for t in pc1.getTransceivers():
        if t.kind == "audio" and audio:
            pc1.addTrack(audio)
        elif t.kind == "video" and video:
            pc1.addTrack(video)

    answer = await pc1.createAnswer()
    await pc1.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc1.localDescription.sdp, "type": pc1.localDescription.type}
        ),
    )


async def publish(request):
    pc2 = RTCPeerConnection()
    pcs.add(pc2)
    # open media source
    audio, video = create_local_tracks()

    if audio:
        pc2.addTrack(audio)
    if video:
        pc2.addTrack(video)

    offer = await pc2.createOffer()
    await pc2.setLocalDescription(offer)
    print(offer)

    # @pc2.on("connectionstatechange")
    # async def on_connectionstatechange():
    #     print("Connection state is %s" % pc2.connectionState)
    #     if pc2.connectionState == "failed":
    #         await pc2.close()
    #         pcs.discard(pc2)
    #

    # answer = await pc2.createAnswer()
    # await pc2.setLocalDescription(answer)
    #
    # return web.Response(
    #     content_type="application/json",
    #     text=json.dumps(
    #         {"sdp": pc2.localDescription.sdp, "type": pc2.localDescription.type}
    #     ),
    # )


async def subscribe(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc2 = RTCPeerConnection()
    pcs.add(pc2)

    @pc2.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc2.connectionState)
        if pc2.connectionState == "failed":
            await pc2.close()
            pcs.discard(pc2)

    # open media source
    audio, video = create_local_tracks()

    await pc2.setRemoteDescription(offer)
    for t in pc2.getTransceivers():
        if t.kind == "audio" and audio:
            pc2.addTrack(audio)
        elif t.kind == "video" and video:
            pc2.addTrack(video)

    answer = await pc2.createAnswer()
    await pc2.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc2.localDescription.sdp, "type": pc2.localDescription.type}
        ),
    )


pcs = set()


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
