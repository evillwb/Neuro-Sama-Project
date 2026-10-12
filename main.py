"""Talk to your AI VTuber.

    python main.py            talk through the mic
    python main.py --text     type instead of talking (handy for testing)
    python main.py --devices  list mics and speakers
"""

import argparse

import config
from neuro.brain import Brain
from neuro.text import SentenceSplitter


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--text", action="store_true", help="type instead of using the mic")
    parser.add_argument("--devices", action="store_true", help="list audio devices and exit")
    parser.add_argument("--no-vts", action="store_true", help="don't connect to VTube Studio")
    args = parser.parse_args()

    if args.devices:
        import sounddevice as sd
        print(sd.query_devices())
        return

    brain = Brain()
    brain.check()

    vts = None
    if config.VTS_ENABLED and not args.no_vts:
        from neuro.vts import VTubeStudio
        vts = VTubeStudio()
        if not vts.connect():
            vts = None

    from neuro.voice import Voice
    voice = Voice(vts)

    ears = None
    if not args.text:
        from neuro.ears import Ears
        ears = Ears()
        ears.calibrate()

    print(f"\n{config.NAME} is ready! {'Type' if args.text else 'Talk'} to her. Ctrl+C to quit.\n")
    try:
        while True:
            if ears:
                print("(listening...)")
                heard = ears.transcribe(ears.listen())
                if not heard:
                    continue
                print(f"You: {heard}")
            else:
                heard = input("You: ").strip()
                if not heard:
                    continue

            print(f"{config.NAME}: ", end="", flush=True)
            splitter = SentenceSplitter()
            for token in brain.reply(heard):
                print(token, end="", flush=True)
                for sentence in splitter.feed(token):
                    voice.say(sentence)
            for sentence in splitter.flush():
                voice.say(sentence)
            print()
            voice.wait()  # Don't listen while she talks, or she'll hear herself.
    except KeyboardInterrupt:
        print("\nBye!")
    finally:
        if vts:
            vts.close()


if __name__ == "__main__":
    main()
