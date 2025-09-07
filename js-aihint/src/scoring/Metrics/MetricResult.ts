export enum MetricStatus {
  INFO = 'INFO',
  SUCCESS = 'SUCCESS',
  WARNING = 'WARNING',
  ERROR = 'ERROR'
}

export interface MetricResultData {
  name: string;
  score: number;
  status: MetricStatus;
  message: string;
  executionTime: number;
  details?: any;
}

export class MetricResult {
  public readonly name: string;
  public readonly score: number;
  public readonly status: MetricStatus;
  public readonly message: string;
  public readonly executionTime: number;
  public readonly details?: any;

  constructor(data: MetricResultData) {
    this.name = data.name;
    this.score = data.score;
    this.status = data.status;
    this.message = data.message;
    this.executionTime = data.executionTime;
    this.details = data.details;
  }

  toJSON(): any {
    return {
      name: this.name,
      score: this.score,
      status: this.status,
      message: this.message,
      execution_time: this.executionTime,
      details: this.details
    };
  }
}
