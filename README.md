[![Software License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/NovelTorpedo/noveltorpedo.svg?branch=master)](https://travis-ci.org/NovelTorpedo/noveltorpedo)

# NovelTorpedo

https://github.com/NovelTorpedo/noveltorpedo

(c) 2017 Brook Boese, Finn Ellis, Jacob Martin, Matthew Popescu,
Rubin Stricklin, and Sage Callon.

NovelTorpedo is web-based searchable database of online serial fiction. Unlike
the many websites which directly host stories, NovelTorpedo follows in the
footsteps of [ComicRocket](http://www.comicrocket.com) as a host-agnostic
index of works which are already being published elsewhere. Authors and
readers can suggest new works to be tracked, and developers can add new
scrapers (or API consumers) to make more hosts available for indexing. We
have many future features planned, including the ability to subscribe to
stories and be notified when they update, or find new works based on existing
preferences. NovelTorpedo will always honor and support the rights of creators,
sending readers to the original publication point rather than mirroring.

NovelTorpedo is licensed under the MIT license, which allows you to copy,
modify, and distribute it with attribution. See LICENSE.txt for details.


## Installation and Usage

NovelTorpedo consists of two major interdependent parts which have their own
documentation: the website (including the database), and the host-specific
scrapers/fetchers which populate it.

To use any part of NovelTorpedo, you need to set up at least the website
backend and the database.

* [Website Documentation](/website)

To add data to its index, you will additionally need to set up the interface
to whatever site you want to get data from.

* [Space Battles Scraper Documentation](/scrapers/Spacebattles)
* [Tumblr Fetcher Documentation](/scrapers/tumblr)


## Contact

We're developing NovelTorpedo for the F16/W17 Portland State University
[CS Capstone](http://wiki.cs.pdx.edu/capstone/), sponsored by Aaron Kurtz
and Jamey Sharp and instructed by Professor Bart Massey.

We're not actively seeking contributions while the capstone is in progress.
That said, if you have questions, comments, or concerns, feel free to
[open an issue](https://github.com/NovelTorpedo/noveltorpedo/issues)!

For a longer-term policy, check back after March 2017.
