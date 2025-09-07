export enum TrustLevel {
  VERY_LOW = 'VERY_LOW',
  LOW = 'LOW',
  MODERATE = 'MODERATE',
  GOOD = 'GOOD',
  HIGH = 'HIGH'
}

export class TrustLevelHelper {
  static getDescription(level: TrustLevel): string {
    switch (level) {
      case TrustLevel.VERY_LOW:
        return 'Very low trust (suspicious, potentially harmful)';
      case TrustLevel.LOW:
        return 'Low trust (unreliable, proceed with caution)';
      case TrustLevel.MODERATE:
        return 'Moderate trust (newer sites, some concerns)';
      case TrustLevel.GOOD:
        return 'Good trust (legitimate businesses, established sites)';
      case TrustLevel.HIGH:
        return 'High trust (verified, highly reputable)';
      default:
        return 'Unknown trust level';
    }
  }

  static getScoreRange(level: TrustLevel): { min: number; max: number } {
    switch (level) {
      case TrustLevel.VERY_LOW:
        return { min: 0, max: 0.2 };
      case TrustLevel.LOW:
        return { min: 0.2, max: 0.4 };
      case TrustLevel.MODERATE:
        return { min: 0.4, max: 0.6 };
      case TrustLevel.GOOD:
        return { min: 0.6, max: 0.8 };
      case TrustLevel.HIGH:
        return { min: 0.8, max: 1.0 };
      default:
        return { min: 0, max: 0 };
    }
  }
}
