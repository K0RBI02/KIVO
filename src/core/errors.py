"""
KIVO Engine
Zentrale Fehlerklassen (EINE Quelle, keine Duplikate mehr)
"""

from __future__ import annotations


class DomainError(Exception):
    """Basisklasse aller Domain-Fehler."""


class EntityNotFoundError(DomainError):
    """Eine Entity wurde nicht gefunden."""


class DuplicateEntityError(DomainError):
    """Eine Entity existiert bereits."""


class InvalidRelationError(DomainError):
    """Eine Relation ist ungueltig."""


class ValidationError(DomainError):
    """Domain-Validierung fehlgeschlagen."""


class ServiceNotFoundError(Exception):
    """Ein Service ist in Container/Registry nicht registriert."""


class DuplicateRegistrationError(Exception):
    """Ein Service ist bereits registriert."""


class EventError(Exception):
    """Fehler im Event-System."""
