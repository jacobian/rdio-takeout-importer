### This can help export your Rdio collection into Spotify saved tracks

**This is entirely crummy, "works for me"-style code. It may work for you,
but it probably won't. Please don't use this unless you're willing to do
some serious debugging and fooling around. If it breaks, I probably can't
help you, sorry.**

Still want to play?

### OK, here's how I did this:

First, you need the same kit as I have:

- Chrome
- Python 2.7 (probably works with other versions, haven't tried).
- [iTerm2 beta version](https://www.iterm2.com/downloads.html) (this is how I did images. you can probably rip this out without much trouble if you don't want to use iTerm2)
- Rdio and Spotify accounts, natch.

Then:

1. Install the [Rdio Enhancer Chrome plugin](https://chrome.google.com/webstore/detail/rdio-enhancer/hmaalfaappddkggilhahaebfhdmmmngf?hl=en)

1. Visit Rdio in Chrome, go to your favorites view, make sure you're in "Album's & Songs" Mode (it'll be a URL like `http://www.rdio.com/people/{YOURNAME}/favorites/albums/`).

1. If Rdio Enhancer is working, you should see a "Export to CSV" button. Click it. **Wait, this takes a long time** (like, 10 minutes for my 1000-ish albums).

1. Create a [Spotify API application on this page](https://developer.spotify.com/my-applications/#!/applications)

1. Modify `r2s.py`, filling in the 4 constants up at the top with the info from the app you created above. The redirect URI can be any valid URL, make sure you hit "save" at the bottom after entering it. When you run the `r2s.py` program it will have you manually copy in the URL that you are redirected to, no server is required.

1. Install your Python kit: `pip install -r requirements.txt`

1. Convert the collection csv into a sqlite db you need for the next step: `python rdio_export_to_sqlite.py`

1. Run the converter! `python r2s.py`. It'll try to match albums in Rdio to equivalents in Spotify. If no results are found, you get a chance to manually enter artist/album for a search. Then, you'll see the best match, and can add it, try the next match, or skip the album entirely (for music you don't want to port over).

### Caveats

Lots, I'm sure. Here are the ones I know of:

- Doesn't do playlists. See http://soundiiz.com/.

- Skips albums with less than 5 tracks saved in Rdio. Tweak on line 38 if `r2s.py` if you like.
