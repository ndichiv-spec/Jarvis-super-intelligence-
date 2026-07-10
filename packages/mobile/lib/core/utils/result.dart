class Result<T> {
  const Result._();

  factory Result.success(T data) = Success<T>;
  factory Result.failure(AppException error) = Failure<T>;
}

class Success<T> extends Result<T> {
  const Success(this.data) : super._();
  final T data;
}

class Failure<T> extends Result<T> {
  const Failure(this.error) : super._();
  final AppException error;
}
