import telepot


class TGBot(telepot.Bot):
    def __init__(self, config):
        """Set TG bot attributes from config file."""
        self.singleMode = config['general']['single_mode'] == 'True'
        config = config['telegram']
        self.sender = config['sender']
        self.chatID = int(config['chatid'])
        self.bot = telepot.Bot(config['token'])

    def setIRCbot(self, bot):
        """Set self.ircbot to bot, assuming it's an IRCbot instance."""
        self.ircbot = bot

    def start(self):
        """Start loop handling incoming TG messages with self.handle."""
        from telepot.loop import MessageLoop
        MessageLoop(self.bot, self.handle).run_forever()

    def handle(self, msg):
        """Process TG message to possible IRCbot output.

        Sends msg formatted with self.formatMessage to self.ircbot if
        msg.chat.id == self.chatID, otherwise prints a failure msg.
        """

        # Function unclear (where is .connected_checker from?).
        if (not self.ircbot.connection.is_connected()):
            self.ircbot.connection.connected_checker()

        print(msg)
        if msg['chat']['id'] == self.chatID:
            self.ircbot.sendMessage(self.ircbot.channel,
                                    self.formatMessage(msg))
        else:
            print('message received from non-handled chat with ID {}'.
                  format(msg['chat']['id']))

    def formatMessage(self, msg):
        """Parse TG message msg to IRC message string.

        Will parse msg.text or msg.stricker.emoji fine, otherwise set a
        'message type not supported' message. On self.singleMode, will return
        only this message body, otherwise will prepend a <>-delimited name;
        either msg.from.username (replace 'username' with whatever is set
        in self.sender via config file), or msg.from.first_name.
        """
        try:
            body = msg['text']
        except KeyError:
            try:
                body = msg['sticker']['emoji']
            except KeyError:
                body = 'message type not supported'
        if self.singleMode:
            return body

        try:
            sender = msg['from'][self.sender]
        except:
            sender = msg['from']['first_name']
        return '<{}> {}'.format(sender, body)

    def send(self, msg):
        """Send message msg as TG message to chat identified by self.chatID."""
        self.bot.sendMessage(self.chatID, msg)
