# -*- coding: utf-8 -*-
import re
import sys

from intelmq.lib import utils
from intelmq.lib.bot import Bot
from intelmq.lib.message import Event

REGEX_IP = "^[^ \t]+"
REGEX_TIMESTAMP = "# ([^ \t]+ [^ \t]+)"


class BruteForceBlockerParserBot(Bot):

    def process(self):
        report = self.receive_message()

        raw_report = utils.base64_decode(report.get("raw"))
        for row in raw_report.splitlines():

            if not row or row.startswith('#'):
                continue

            event = Event(report)

            match = re.search(REGEX_IP, row)
            if match:
                ip = match.group()

            match = re.search(REGEX_TIMESTAMP, row)
            if match:
                timestamp = match.group(1) + " UTC"
                continue

            if not timestamp:
                raise ValueError('No timestamp found.')

            event.add('time.source', timestamp)
            event.add('source.ip', ip)
            event.add('classification.type', 'brute-force')
            event.add("raw", row)

            self.send_message(event)
        self.acknowledge_message()

if __name__ == "__main__":
    bot = BruteForceBlockerParserBot(sys.argv[1])
    bot.start()
