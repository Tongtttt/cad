# CAD Extension Guide

This repository is the AutoCAD MCP server core plus the local skill extension.

## What is included

- Core AutoCAD MCP server
- File IPC / ezdxf backends
- Local skill extension for visible AutoCAD workflows
- Portrait bridge and ComfyUI integration notes
- AutoCAD helper LISP scripts

## Default usage model

If a request is not explicitly a portrait / character tracing task, treat it as engineering / chemical drafting.

## Portrait mode

Use only when the user clearly says they are drawing a person or tracing a character image.

## Engineering mode

This is the default. Treat ambiguous CAD tasks as rigorous engineering drafting.

## Local bridge notes

The local bridge scripts under `skill-extension/autocad-direct-drawing/` are meant to be adapted per machine.
Set the local AutoCAD, ComfyUI, and workspace paths before running them on a new system.

## ComfyUI

A local ComfyUI installation is expected on the target machine. Update the bridge script path(s) to match your environment.

## Public release note

This repository should not include licensed AutoCAD installation files or other redistributable-problematic assets. Keep the repo focused on source, scripts, docs, and portable configuration.
