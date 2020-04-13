# Mail Flagger

Mail Flagger is a program that flags selected emails in your inbox, typically when a relevant payment is made. This gives the sender a possibility to bring attention to his message and to compensate time spent by the receiver on reading and eventual responding. Potential users include, but are not limited to:

* specialists and people who want to benefit from their knowledge;
* famous people and fans who want to somehow connect with them;
* customers and 

Mail Flagger is free software, licensed under [Apache License 2.0](https://apache.org/licenses/LICENSE-2.0). It is a desktop application and your email password is saved locally on your computer, if at all.

## How to use

1. Install [Python](https://www.python.org) (version 3.8 or newer is required).
2. Download a [Mail Flagger release](#) for your platform.
3. Run the downloaded file, fill in the configuration and start the `daemon` command.
4. Instruct your senders.

Specific steps for senders depend on the payment method, but typically they will need to encompass a search query that specifies which message they want to get flagged. Its syntax is the same as the syntax for [IMAP search command](https://tools.ietf.org/html/rfc3501#section-6.4.4). An example query:

```
SINCE 20-Mar-2020 FROM john.doe@example.com UNANSWERED`
```

Mail Flagger automatically adds the `UNFLAGGED` search term to the provided query.

### Payment methods

The daemon only listens and waits until something tells it to flag a message, it does nothing on its own initiative. To make it do something, you need a flagging provider, typically tied to a payment method(s). Two of them are bundled inside the default release packages, but the overall mechanism is extensible and allows writing providers in various programming languages.

#### Banking

This provider adds a subcommand that allows importing a file in the MT940 format containing a list of transactions. Daemon needs to be running separately for this to work. A query needs to be encompassed in transaction message (optionally with a specific prefix to distinguish it from other transfers).

Manual export and import is cumbersome, but it is a typical limitation for banking systems, which do not facilitate integration for ordinary users. For a more smooth experience with live transaction processing, consider using cryptocurrencies.

#### Ercoin

This provider adds an optional daemon coroutine that runs along the main daemon and live monitors for [Ercoin](https://ercoin.tech) transactions. A query needs to be encompassed in transaction message.

## Advanced usage

### Custom installation

Mail Flagger can be installed using [pip](https://pip.pypa.io):

```
pip install mailflagger
```

For GUI support, install `mailflagger[GUI]` instead of the above. Two plugins bundled in the standard release are `mailflagger_banking` and `mailflagger_ercoin`.

### Command line

If you don’t want to use GUI, either make a custom installation without the GUI support or provide any argument to the `mailflagger` command.

### Creating custom providers

#### Generic method

The daemon exposes itself as a [ZeroMQ](https://zeromq.org) server. To flag a message, it is sufficient to connect to it and send a [MessagePack](https://msgpack.org)-encoded map containing IMAP query associated with the `"query"` key. A reply will be another map containing key `"processed"` (should be `true`).

#### Python plugins

Provider can be embedded into the main Main Flagger program either as subcommands or as coroutines which will be started with the daemon. When writing plugins, the `mailflagger.client.Client` class should be helpful. It wraps the ZeroMQ connection and message packing and unpacking.

When defining plugin-specific configuration options, remember to avoid name clashes and potential name clashes (with other plugins).

When we write about “default arguments”, we mean either default argument values or values saved in a configuration file.

##### Subcommands

This type of plugin needs to specify a `mailflagger.plugins.commands` entry point which points to an object which defines the following function attributes:

* `modify_subparser` (accepting subparser) — optional, used to add plugin-specific configuration options.
* `run` (accepting parsed arguments) — used to do the actual job.
* `command_help` (accepting default arguments) — optional, it returns help for the subcommand.

See the `mailflagger_banking` plugin for an example.

##### Daemon coroutines

This type of plugin needs to specify a `mailflagger.plugins.daemon` entry point which points to an object which defines the following function attributes:

* `modify_subparser` (accepting subparser) — optional, used to add plugin-specific configuration options to the daemon subparser.
* `daemon_coroutines` (accepting parsed arguments) — returning an iterable of coroutines that shall be started along with the server daemon.

See the `mailflagger_ercoin` plugin for an example.
