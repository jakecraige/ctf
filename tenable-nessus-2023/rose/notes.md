# Rose
> The owner of the site shut down sign ups for some reason, but we've got a backup
> of the code.
> See if you can get access and get /home/ctf/flag.txt
> https://nessus-rose.chals.io/

## Analysis Notes
- `__init__.py` has default secret key for Flask app
  Might be able to do this to forge session.
  Session needs `name` to work
- signup routes are disabled
- `/dashboard` uses `render_template_string` with the session name without
    escaping. If we can forge this we can template inject

