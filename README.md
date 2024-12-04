# Genitest

### What is it?

A standalone unit test creator that takes a python file and creates tests for it or any of the multiple files you select.  (Yes, copilot can do this too, but this is a command line tool that doesn't require an IDE)

### Requirements and Options:

In `~/.zshrc` you must have the following environmental variables:

* OPENAI_API_KEY
	* the key to use with chatgpt api
* CONTEXT_FILE (optional)
	* the file that tells the bot what to do when writing tests if there is anything specific.  If this isn't set it will default to the base context (which is ok for most use cases).

### Running the script

```
./genitest
```

