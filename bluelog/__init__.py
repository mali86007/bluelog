import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError
from bluelog.views.admin import admin_bp
