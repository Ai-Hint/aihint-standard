<?php
namespace AIHint\Scoring\Metrics;

enum MetricStatus: string
{
    case SUCCESS = 'success';
    case WARNING = 'warning';
    case ERROR = 'error';
    case SKIPPED = 'skipped';
}
