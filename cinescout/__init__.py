"""Defines cinescout directory as package, i.e. can be imnported. 
File executed when package imported."""

print("Executing __init__.py...")

from flask import Flask

print("Flask successfully imported.")

app = Flask(__name__)

print("app object created.")

from cinescout import routes

print("routes imported")

print("End of __init__.py")
