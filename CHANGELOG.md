ALPHA v0.0.0.0
    - Created <class Server> in server.py
        - Added ability to send files (including images)
        - Streamlined file sending to automatically locate files in designated folders
    - Set up home.html, mostly for testing at this point
    - Added a bunch of files, most empty, in preparation for future construction

ALPHA v0.0.0.1
    - Renamed home.html to test.html; created a new home.html for actual home-page use
    - Implemented formal <class Response> in server.py for better compatibility
    - Added proper response codes for the server in <class Response>
    - Added <class Log> in server.py to track events
    - Gave .md extensions to README and CHANGELOG

ALPHA v0.0.0.2
    - Minor edits to README.md
    - Changed <class Log> to write to a new file (timestamped) when it dumps
        - Created logs folder, deleted log.log.
    - Copied current test code over to main.py
    - Commented server.py
    - Added cookie support to parse() in <class Server> (really should have had that all along)

ALPHA v0.0.0.3
    - Fixed some issues with cookie management
    - Work has begun on home.html (recommend we continue in a real web editor, manual CSS will be tough)