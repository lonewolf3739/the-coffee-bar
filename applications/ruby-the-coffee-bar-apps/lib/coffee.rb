$stdout.sync = true

require 'rubygems'
require 'bundler/setup'
require 'sinatra'
require 'json'

require_relative "opentelemetry-instrumentation"
require_relative "version"


class Coffee < Sinatra::Base
    set :port, ENV['PORT'] || 9091
    set :bind, ENV['HOST'] || 'coffee-svc'

    post '/get_coffee' do
        span_id = OpenTelemetry::Trace.current_span.context.hex_span_id
        trace_id = OpenTelemetry::Trace.current_span.context.hex_trace_id

        payload = JSON.parse(request.body.read)
        puts "INFO - Received order for coffee grains #{payload['coffee']} - trace_id=#{trace_id} - span_id=#{span_id}"

        content_type :json

        if payload['coffee'] < 0
            status 502
            body "Lack of coffee"
            puts "ERROR - Lack of coffee grains in amount #{payload['coffee']} - trace_id=#{trace_id} - span_id=#{span_id}"

            ## Add event into span
            OpenTelemetry::Trace.current_span.add_event("exception", attributes: { 'exception.code' => '502', 'exception.message' => 'Lack of coffee' })
        else
            body "Coffee provided"
            puts "INFO - Coffee grains in amount #{payload['coffee']} provided - trace_id=#{trace_id} - span_id=#{span_id}"
        end
    end

    run! if __FILE__ == $0
end
