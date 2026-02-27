"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for domain-layer exceptions."""


class ValidationError(DomainError):
    """Raised when an entity or value object violates domain rules."""


class ConflictError(DomainError):
    """Raised when an operation would violate uniqueness or state constraints."""


class NotFoundError(DomainError):
    """Raised when an expected entity cannot be located."""

