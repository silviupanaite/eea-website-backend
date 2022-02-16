FROM eeacms/eea-website-backend
COPY sources.ini /app/
RUN bin/mxdev -c sources.ini \
 && bin/pip install -r requirements-mxdev.txt $(PIP_PARAMS)
