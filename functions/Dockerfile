FROM node:18-slim

WORKDIR /app

# Install Firebase CLI globally
RUN npm install -g firebase-tools

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port for Firebase emulator
EXPOSE 5001

# Start Firebase emulator
CMD ["firebase", "emulators:start", "--only", "functions", "--port", "5001"] 