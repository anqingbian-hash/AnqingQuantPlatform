#!/bin/bash
python3 -c "
from real_data_app import app
app.run(host='0.0.0.0', port=80, debug=False)
" > real_data_app.log 2>&1 &
